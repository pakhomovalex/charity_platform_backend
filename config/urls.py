from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from users.views import (
    CustomRegisterView,
    CustomPasswordResetView,
    CurrentUserProfileView,
    GoogleLogin,
)


from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordChangeView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # 1. Адмін-панель
    path("admin/", admin.site.urls),
    # 2. API наших додатків
    path("api/v1/projects/", include("projects.urls")),
    path("api/v1/users/", include("users.urls")),
    # 3. АУТЕНТИФІКАЦІЯ
    # Реєстрація
    path(
        "api/v1/auth/registration/",
        CustomRegisterView.as_view(),
        name="rest_register",
    ),
    # Скидання паролю
    path(
        "api/v1/auth/password/reset/",
        CustomPasswordResetView.as_view(),
        name="rest_password_reset",
    ),
    # Профіль користувача
    path("api/v1/profile/", CurrentUserProfileView.as_view(), name="my_profile"),
    # Соціальна аутентифікація
    path("api/v1/auth/google/", GoogleLogin.as_view(), name="google_login"),
    # Стандартні ендпоінти від dj-rest-auth
    path("api/v1/auth/login/", LoginView.as_view(), name="rest_login"),
    path("api/v1/auth/logout/", LogoutView.as_view(), name="rest_logout"),
    path(
        "api/v1/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/v1/auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "api/v1/auth/password/change/",
        PasswordChangeView.as_view(),
        name="password_change",
    ),
    # 4. Документація API
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Налаштування для медіа файлів
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
