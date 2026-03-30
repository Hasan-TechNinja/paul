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
from subscription.models import UserSubscription, ThemeSubscription
from program.models import Theme
from deep_translator import GoogleTranslator

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
        RegisterOTP.objects.filter(email=email).delete()
        RegisterOTP.objects.create(email=email, otp=code, created_at=timezone.now())
        
        return Response({'message': 'Registration successful. Check OTP in your email to verify your account.'}, status=status.HTTP_200_OK)


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


class SocialLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        full_name = request.data.get('full_name', '')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # We ensure emails are lowercased for consistency
        email = email.lower().strip()

        # Check if user already exists
        user = User.objects.filter(email=email).first()

        if user:
            # Case 1 & 2: User exists
            if not user.is_active:
                user.is_active = True
                user.save()
            
            # Ensure profile exists
            from .models import Profile
            Profile.objects.get_or_create(user=user, defaults={'full_name': full_name or email.split('@')[0]})
            
            message = 'Login successful.'
        else:
            # Case 3: User doesn't exist
            # Create a new active user
            user = User.objects.create_user(
                email=email,
                username=email, # Assuming username uses email
                is_active=True
            )
            # Set an unusable password so they can only log in via social auth
            # or issue a "forgot password" reset later if they want a manual password.
            user.set_unusable_password()
            user.save()

            from .models import Profile
            Profile.objects.create(user=user, full_name=full_name or email.split('@')[0])
            
            message = 'User created and logged in successfully.'

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': message,
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
        profile, created = Profile.objects.get_or_create(user=user)

        # Fetch subscription status
        subscription = UserSubscription.objects.filter(user=user).first()
        is_pro = bool(subscription and subscription.is_pro_active)

        purchased_themes = []
        if is_pro:
            # If Pro, they own all themes
            themes = Theme.objects.all()
            purchased_themes = list(themes.values_list('id', flat=True))
        else:
            # If Basic/Single, show only themes they have an active subscription for
            active_theme_subs = ThemeSubscription.objects.filter(
                user=user, is_active=True
            ).select_related('theme')
            
            # Auto-expire stale records if needed before returning
            now = timezone.now()
            purchased_themes = []
            for ts in active_theme_subs:
                if ts.end_date > now:
                    if ts.theme:
                        purchased_themes.append(ts.theme.id)
                else:
                    ts.is_active = False
                    ts.save(update_fields=['is_active'])

        return Response({
            'email': user.email,
            'full_name': profile.full_name,
            'image': profile.image.url if profile.image else None,
            'is_subscribed': is_pro,
            'purchased_themes': purchased_themes,
        }, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)

        full_name = request.data.get('full_name')
        if full_name is not None:
            profile.full_name = full_name
            
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
        elif 'image' in request.data and request.data['image'] is None:
             profile.image = None

        profile.save()

        return Response({
            'message': 'Profile updated successfully',
            'email': user.email,
            'full_name': profile.full_name,
            'image': profile.image.url if profile.image else None,
        }, status=status.HTTP_200_OK)



class TranslateTextView(APIView):
    def post(self, request):
        target_lang = request.data.get('lang')
        texts = request.data.get('texts')

        if not target_lang or not texts:
            return Response(
                {'error': 'lang and texts fields are required in the JSON payload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(texts, dict):
            return Response(
                {'error': 'texts must be a dictionary of key-value pairs'},
                status=status.HTTP_400_BAD_REQUEST
            )

        translated_texts = {}
        try:
            # We use deep_translator's GoogleTranslator to perform the translation
            translator = GoogleTranslator(source='auto', target=target_lang)
            for key, text in texts.items():
                if isinstance(text, str) and text.strip():
                    translated_texts[key] = translator.translate(text)
                else:
                    translated_texts[key] = text
                
            return Response({
                'lang': target_lang,
                'texts': translated_texts
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Translation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )