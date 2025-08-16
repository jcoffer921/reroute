# settings.py — top of file
import os                         # ← required for os.getenv
from pathlib import Path          # ← if you use BASE_DIR = Path(...)
import dj_database_url            # ← since you call dj_database_url.config(...)

BASE_DIR = Path(__file__).resolve().parent.parent  # Define BASE_DIR for static/media paths

# make sure these exist and match your package name
ROOT_URLCONF = "reroute.urls"
WSGI_APPLICATION = "reroute.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Add your project-level template dirs here (keep APP_DIRS=True too)
        "DIRS": [
            BASE_DIR / "templates",           # if you have a /templates folder
            BASE_DIR / "main" / "templates",  # you do have /main/templates/**
        ],
        "APP_DIRS": True,  # looks in each app's /templates as well
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",   # REQUIRED (admin + allauth)
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Debug & environment flags ---
DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # was hardcoded True
RENDER = os.getenv("RENDER", "") != ""                 # Render sets RENDER="true" in env

# Helpers to parse comma-separated env vars safely
def _csv_env(name, default):
    raw = os.getenv(name, default)
    return [h.strip() for h in raw.split(",") if h.strip()]

ALLOWED_HOSTS = _csv_env(
    "ALLOWED_HOSTS",
    ".onrender.com,reroutejobs.com,www.reroutejobs.com,localhost,127.0.0.1",
)

CSRF_TRUSTED_ORIGINS = _csv_env(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.onrender.com,https://reroutejobs.com,https://www.reroutejobs.com",
)

# Behind Render’s proxy:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Installed apps ---
INSTALLED_APPS = [
    'main',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'resumes',
    'dashboard',
    'blog',
    'core',
    'profiles',
    'job_list',
    'resources',
    'widget_tweaks',
    # 'geopy',   # ❌ remove: geopy is not a Django app
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

# --- Middleware (WhiteNoise directly after SecurityMiddleware) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # moved up
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# --- Static files / WhiteNoise storage (Django 4/5 style) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'main' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- Email (env-driven; console in DEBUG) ---
EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend'
    if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_RECEIVER_EMAIL = os.getenv('CONTACT_RECEIVER_EMAIL', EMAIL_HOST_USER)

# --- Allauth tweaks ---
ACCOUNT_EMAIL_VERIFICATION = "none" if DEBUG else "optional"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if not DEBUG else 'http'

ACCOUNT_LOGIN_METHODS = ["email", "username"]          # new-style
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]

# --- reCAPTCHA via env (no secrets in code) ---
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')

# --- Production security flags ---
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
