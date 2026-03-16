'use strict';

/**
 * Theme Subscription Admin Script
 * ---------------------------------
 * When a Pro plan is selected in the ThemeSubscription add/change form,
 * the "Theme" field is automatically hidden (Pro plans grant access to ALL
 * themes, so per-theme selection is irrelevant).
 *
 * When a Basic plan is selected, the Theme field is shown again.
 *
 * Strategy:
 *   1. Fetch plan types from a server-side JSON endpoint so we never rely
 *      on brittle text-matching.
 *   2. Poll for django.jQuery availability to avoid script load-order issues.
 */

(function () {

    var MAX_WAIT_MS = 5000;   // give up after 5 s
    var POLL_INTERVAL_MS = 50;
    var elapsed = 0;

    function waitForjQuery(callback) {
        var $ = (window.django && window.django.jQuery) || window.jQuery;
        if ($) {
            callback($);
        } else if (elapsed < MAX_WAIT_MS) {
            elapsed += POLL_INTERVAL_MS;
            setTimeout(function () { waitForjQuery(callback); }, POLL_INTERVAL_MS);
        } else {
            console.error('theme_subscription.js: jQuery not available after ' + MAX_WAIT_MS + ' ms. Giving up.');
        }
    }

    function run($) {

        var proPlanIds = [];

        // ── Helpers ──────────────────────────────────────────────────────────

        function getThemeRow() {
            // Django admin wraps each field in .form-row.field-<fieldname>
            return $('#id_theme').closest('.form-row.field-theme, .form-row, .field-theme');
        }

        function toggleThemeField() {
            var selectedId = parseInt($('#id_plan').val(), 10);
            var $row = getThemeRow();

            if (proPlanIds.indexOf(selectedId) !== -1) {
                // Pro plan ── hide theme field and clear its value
                $row.hide();
                $('#id_theme').val('');
            } else {
                // Basic / unselected ── show theme field
                $row.show();
            }
        }

        // ── Fetch plan types from the server ─────────────────────────────────

        function loadPlanTypes() {
            $.ajax({
                url: '/admin/subscription/themesubscription/plan-types/',
                dataType: 'json',
                success: function (data) {
                    proPlanIds = data.pro_plan_ids || [];
                    toggleThemeField();        // apply initial state
                },
                error: function () {
                    // Fallback: parse option text for "(pro)"
                    console.warn('theme_subscription.js: Could not reach plan-types endpoint. Using text fallback.');
                    $('#id_plan option').each(function () {
                        if ($(this).text().toLowerCase().indexOf('(pro)') !== -1) {
                            var id = parseInt($(this).val(), 10);
                            if (!isNaN(id)) { proPlanIds.push(id); }
                        }
                    });
                    toggleThemeField();
                }
            });
        }

        // ── Initialise ───────────────────────────────────────────────────────

        function init() {
            var $planSelect = $('#id_plan');
            if (!$planSelect.length) {
                return;   // not on ThemeSubscription add/change page
            }

            $planSelect.on('change', toggleThemeField);
            loadPlanTypes();
        }

        // Run after the DOM is ready
        $(document).ready(init);
        // Also try immediately in case DOM is already ready
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            init();
        }
    }

    // Kick everything off once jQuery (Django's or global) is available
    waitForjQuery(run);

})();
