# settings.py — top of file
import os                         # ← required for os.getenv
from pathlib import Path          # ← if you use BASE_DIR = Path(...)
import dj_database_url            # ← since you call dj_database_url.config(...)
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent  # Define BASE_DIR for static/media paths

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-secret")

# ---------- DATABASES ----------
# Use Postgres when DATABASE_URL is present (Render/production),
# otherwise default to local SQLite for development.
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600
    )
}

# (Optional but good hygiene)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# make sure these exist and match your package name
ROOT_URLCONF = "reroute.urls"
WSGI_APPLICATION = "reroute.wsgi.application"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'main' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Provide IS_EMPLOYER and DASHBOARD_URL to all templates
                'main.context_processors.role_flags',
            ],
        },
    },
]

# ---------- DEBUG / LOGGING ----------
DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # was hardcoded True
#DEBUG = False
RENDER = os.getenv("RENDER", "") != ""                 # Render sets RENDER="true" in env

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{levelname}] {asctime} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}
# During emergency prod debugging you can also enable this (remove after):
# DEBUG_PROPAGATE_EXCEPTIONS = True

# ---------- HOSTS / CSRF ----------
# Helpers to parse comma-separated env vars safely
def _csv_env(name, default):
    raw = os.getenv(name, default)
    return [h.strip() for h in raw.split(",") if h.strip()]

ALLOWED_HOSTS = ['reroute-backend.onrender.com', 'reroutejobs.com', "www.reroutejobs.com", 'localhost', '127.0.0.1', '10.220.68.190', '10.220.71.47']

CSRF_TRUSTED_ORIGINS = [
    "https://reroute-backend.onrender.com",
    "https://reroutejobs.com",
    "https://www.reroutejobs.com",
    "http://localhost",
    "http://127.0.0.1",
]
# Behind Render’s proxy:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ---------- APPS ----------
INSTALLED_APPS = [
    'main',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # your apps
    'resumes',
    'dashboard',
    'blog',
    'core',
    'profiles',
    'job_list',
    'resources',

    # third-party
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap4',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

# Helpful in dev: let Django serve app static without conflicts
if DEBUG:
    INSTALLED_APPS = ['whitenoise.runserver_nostatic'] + INSTALLED_APPS

# ✅ Sites framework required by allauth to resolve domains
SITE_ID = 1

# ---------- AUTH / ALLAUTH ----------
# Enable allauth backend alongside Django's default
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# If you’re on allauth ≥ 0.63, these “new style” settings are valid.
# If your Render build pins an older allauth, either upgrade or
# switch to legacy equivalents (see comments below).
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# Ensure emails are required for signup and verification flows
# If using allauth ≥ 0.63 new-style settings, email is already in SIGNUP_FIELDS.
# Keep legacy flags for compatibility if version drifts.
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if not DEBUG else 'http'

# New-style (allauth ≥ 0.63):
ACCOUNT_LOGIN_METHODS = ["email", "username"]
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]

# Legacy (ONLY if you’re on old allauth; comment out the two above and use these):
# ACCOUNT_AUTHENTICATION_METHOD = "username_email"
# ACCOUNT_USERNAME_REQUIRED = True
# ACCOUNT_EMAIL_REQUIRED = True

# ---------- CRISPY FORMS ----------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# ---------- MIDDLEWARE ----------
# WhiteNoise must be right after SecurityMiddleware in MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # must be early for static
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'main.middleware.EnforceVerifiedEmailMiddleware',
    'reroute.security_headers.SecurityHeadersMiddleware',
    'core.middleware.pageviews.PageViewMiddleware',
]

# ---------- STATIC / MEDIA ----------
# Static files (CSS, JS, images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'main' / 'static']  # app-level assets during build
STATIC_ROOT = BASE_DIR / 'staticfiles'             # where collectstatic writes

# Use WhiteNoise + Manifest storage for cache-busting in production.
# If you hit a "Missing staticfiles manifest" error after deploy,
# temporarily switch to CompressedStaticFilesStorage, redeploy to verify,
# then switch back and ensure collectstatic runs in your Build Command.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# Temporary fallback (comment out the Manifest line above and uncomment below if needed):
# STORAGES = {
#     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
#     "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
# }

# ---------- EMAIL ----------
EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend'
    if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_HOST_USER = 'support@reroutejobs.com' 
EMAIL_HOST_PASSWORD = 'rfwkrwlvqomsmcry'  # Use App Password (never your real one)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_RECEIVER_EMAIL = 'support@reroutejobs.com' 

# ---------- SECURITY (production) ----------
# These are enabled only when DEBUG is False (i.e., on Render)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000      # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True          # allows you to submit to hstspreload.org later

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Google reCAPTCHA settings
if DEBUG:
  # Local development keys
    RECAPTCHA_SITE_KEY = '6LchCXsrAAAAAJUK4ipb6_vBjR84Yn_1HfbUeXZQ'
    RECAPTCHA_SECRET_KEY = '6LchCXsrAAAAAPm9n82MxoLQXRwUucSybpFcmfEV'
else:
    # Live Keys for reroutejobs.com
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')

# Send anonymous users here when @login_required triggers
LOGIN_URL = '/login/'

# Where to land after successful login
LOGIN_REDIRECT_URL = '/dashboard/'

# Where to land after logout (optional)
LOGOUT_REDIRECT_URL = '/'
