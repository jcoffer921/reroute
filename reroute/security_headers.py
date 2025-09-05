# security_headers.py  (put in your project and add to MIDDLEWARE after SecurityMiddleware)
from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # --- Content Security Policy ---
        # Start with a conservative baseline. Switch 'report-only' to 'Content-Security-Policy'
        # after you verify in the browser console that nothing breaks.
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests"  # auto-upgrade http assets to https
        )
        response.headers.setdefault("Content-Security-Policy", csp)

        # --- Permissions-Policy: lock down browser features ---
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

        return response
