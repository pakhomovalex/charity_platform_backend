# config/settings.py

from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "True") == "True"
RENDER_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_HOSTNAME]
else:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = [f"https://{RENDER_HOSTNAME}"] if RENDER_HOSTNAME else []


# --- Application definition ---
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party apps
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "storages",
    "imagekit",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "corsheaders",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # My apps
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "projects.apps.ProjectsConfig",
]

MIDDLEWARE =[
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "core/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database ---
# DATABASES = {
#     "default": dj_database_url.config(
#         default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
#         conn_max_age=600,
#     )
# }

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production (Render + Neon)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True  # Важно для Neon!
        )
    }
else:
    # Local development (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- Auth ---
AUTH_USER_MODEL = "users.CustomUser"
SESSION_COOKIE_AGE = 86400
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]
AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
)
SITE_ID = 1

# --- Internationalization ---
LANGUAGE_CODE = "uk-ua"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

# --- Static & Media Files ---
STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

if DEBUG:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    AWS_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = (
        f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
    )
    AWS_S3_CUSTOM_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN")
    AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {},
        },
        "staticfiles": {
            # "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
            "BACKEND": "whitenoise.storage.WhiteNoiseStorage"
        },
    }
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    # STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

# --- CORS ---
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", # https://pidtrumyi.vercel.app/
     "http://localhost:3000"
).split(",")

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
    "USER_DETAILS_SERIALIZER": "users.serializers.CurrentUserSerializer",
    "REGISTER_SERIALIZER": "users.serializers.CustomRegisterSerializer",
    "PASSWORD_RESET_SERIALIZER": "users.serializers.FinalPasswordResetSerializer",
}

# --- Frontend URL ---
CLIENT_URL = os.getenv("CLIENT_URL", # https://pidtrumyi.vercel.app/
 "http://localhost:3000"
 )
PASSWORD_RESET_URL_TEMPLATE = (
    f"{CLIENT_URL}/password-reset-confirm/{{uid}}/{{token}}/"
)

# --- django-allauth ---
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "none"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# --- DRF-Spectacular ---
SPECTACULAR_SETTINGS = {
    "TITLE": "Charity Platform API",
    "DESCRIPTION": "Документація для API благодійної платформи.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "PREPROCESSING_HOOKS": ["core.spectacular_hooks.pre_processing_hook"],
}

# --- Jazzmin ---
JAZZMIN_SETTINGS = {
    "site_title": "Кабінет",
    "site_header": "Підтримай",
    "site_brand": "Благодійна платформа",
    "site_logo": "img/logo.png",
    "welcome_sign": "Вітаємо!",
    "copyright": "Підтримай © 2024",
    "hide_apps": [
        "auth",
        "authtoken",
        "account",
        "socialaccount",
        "sites",
        "token_blacklist",
    ],
    "order_with_respect_to": ["users", "projects"],
    "topmenu_links": [
        {
            "name": "На Головну",
            "url": CLIENT_URL,
            "new_window": True
        },
    ],
    "icons": {
        "users.CustomUser": "fas fa-user-circle",
        "projects.Project": "fas fa-hands-helping",
        "projects.Category": "fas fa-tags",
    },
    "custom_css": "css/custom_admin.css",
    "custom_js": "js/custom_admin.js",
}
JAZZMIN_UI_TWEAKS = {
    "theme": "default",
    "dark_mode_theme": None,
    "sidebar": "sidebar-light-primary",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "accent": "accent-primary",
}

# --- Email ---

EMAIL_BACKEND = "config.email_backends.SendGridBackend"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "pakhomov.alex.v@gmail.com")

# --- Logging ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
