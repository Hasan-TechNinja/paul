from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import random
from django.utils import timezone
from .models import Profile

User = get_user_model()

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not email:
            return Response({'error': "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not password:
            return Response({'error': "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return Response({'error': 'Password does not match'}, status=status.HTTP_400_BAD_REQUEST)

        full_name = request.data.get('full_name', email.split('@')[0])

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'error': 'User with this email already exists and is active'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # User exists but is inactive, update the password just in case they changed it during this retry
                user.set_password(password)
                user.save()
                
                # Ensure profile exists
                from .models import Profile
                Profile.objects.get_or_create(user=user, defaults={'full_name': full_name})
        else:
            # Create a new inactive user
            user = User.objects.create_user(
                email=email,
                username=email, # Assuming username is required, usually email is passed or username isn't used.
                password=password,
                is_active=False
            )
            from .models import Profile
            Profile.objects.create(user=user, full_name="Full Name")

        # Generate OTP
        code = str(random.randint(1000, 9999)) # 4 digit OTP for better security
        
        # Send OTP via email
        try:
            send_mail(
                'Register OTP Verification',
                f'Your OTP is {code}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # If email fails to send, deleting user might be an option, but keeping it inactive works too. 
            pass

        # Save OTP in DB
        from .models import RegisterOTP
        RegisterOTP.objects.create(email=email, otp=code, created_at=timezone.now())
        
        return Response({'message': 'Registration successful. Check your email to verify your account.'}, status=status.HTTP_200_OK)


class VerifyView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import RegisterOTP
        
        # Find the latest OTP for this email
        otp_record = RegisterOTP.objects.filter(email=email, otp=otp).order_by('-created_at').first()

        if not otp_record:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.expired():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Activate the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Clean up OTP records for this email
        RegisterOTP.objects.filter(email=email).delete()

        return Response({
            'message': 'Account verified successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({'error': 'Account is not active. Please verify your email.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return Response({'error': 'Current password, new password, and confirm password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'error': 'Current password does not match.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'New password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not user.is_active:
            return Response({'error': 'Account is not active. Please verify your email.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OTP
        code = str(random.randint(1000, 9999))
        
        # Send OTP via email
        try:
            send_mail(
                'Forgot Password OTP Verification',
                f'Your OTP is {code}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            pass
        
        # Save OTP in DB
        from .models import RegisterOTP
        RegisterOTP.objects.create(email=email, otp=code, created_at=timezone.now())
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not email or not otp or not new_password or not confirm_password:
            return Response({'error': 'Email, OTP, new password, and confirm password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)

        from .models import RegisterOTP
        
        # Find the latest OTP for this email
        otp_record = RegisterOTP.objects.filter(email=email, otp=otp).order_by('-created_at').first()

        if not otp_record:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.expired():
            return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Reset the password
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        # Clean up OTP records for this email
        RegisterOTP.objects.filter(email=email).delete()

        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)    



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)



class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        return Response({
            'email': user.email,
            'full_name': profile.full_name,
            'image': profile.image.url if profile.image else None,
        }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        
        full_name = request.data.get('full_name')
        image = request.data.get('image')

        if full_name:
            profile.full_name = full_name
        
        if image:
            profile.image = image
        
        profile.save()
        
        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
    