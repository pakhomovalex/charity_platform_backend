from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.db.models import Count, Q, Prefetch
from .models import CustomUser
from projects.models import Project, ProjectImage
from .serializers import (
    AuthorListSerializer,
    AuthorDetailSerializer,
    CurrentUserSerializer,
    CustomRegisterSerializer,
    FinalPasswordResetSerializer,
)
from dj_rest_auth.utils import jwt_encode
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.conf import settings

# --- 1. ПУБЛІЧНІ ПРОФІЛІ АВТОРІВ ---


@extend_schema_view(
    list=extend_schema(
        summary="Отримати список авторів",
        description="Повертає список авторів, у яких є хоча б один активний проєкт.",
        tags=["Authors"],
    ),
    retrieve=extend_schema(
        summary="Отримати публічний профіль автора",
        description="Повертає повну публічну інформацію про автора, включаючи список його активних проєктів.",
        tags=["Authors"],
    ),
)
class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для перегляду публічних профілів авторів.
    """

    def get_queryset(self):
        queryset = CustomUser.objects.annotate(
            project_count=Count(
                "projects", filter=Q(projects__status=Project.Status.ACTIVE)
            )
        )

        queryset = queryset.prefetch_related(
            "specialization",
            Prefetch(
                "projects",
                queryset=Project.objects.filter(
                    status=Project.Status.ACTIVE
                ).prefetch_related(
                    Prefetch(
                        "images",
                        queryset=ProjectImage.objects.order_by("order"),
                    )
                ),
            ),
        )

        if self.action == "list":
            return queryset.filter(project_count__gt=0)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AuthorListSerializer
        return AuthorDetailSerializer


# --- 2. ПРОФІЛЬ ПОТОЧНОГО КОРИСТУВАЧА ---


@extend_schema(
    summary="Отримати або оновити свій профіль",
    description="""
GET: Повертає дані поточного користувача.
PATCH/PUT: Оновлює дані. Для текстових полів використовуйте application/json. 
Для завантаження аватара використовуйте multipart/form-data з полем 'avatar'.
У відповідь завжди повертається повний оновлений об'єкт користувача.
    """,
    tags=["Profile (Me)"],
)
class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    """
    Єдиний ендпоінт для роботи з профілем поточного користувача.
    """

    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]  # Приймає і JSON, і файли

    def get_object(self):
        return self.request.user

class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.AllowAny]

class IsProfileOwnerOrAdmin(permissions.BasePermission):
    """
    Только владелец профиля или админ может редактировать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj == request.user or request.user.is_superuser

# --- 3. АУТЕНТИФІКАЦІЯ ---


@extend_schema(
    summary="Реєстрація нового користувача",
    tags=["Authentication"],
)
class CustomRegisterView(generics.CreateAPIView):
    serializer_class = CustomRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        access_token, refresh_token = jwt_encode(user)
        user_data = CurrentUserSerializer(
            user, context=self.get_serializer_context()
        ).data
        data = {
            "user": user_data,
            "access": str(access_token),
            "refresh": str(refresh_token),
        }
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    summary="Вхід через Google",
    tags=["Authentication"],
)
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.CLIENT_URL
    client_class = OAuth2Client


@extend_schema(
    summary="Запит на скидання паролю",
    tags=["Authentication"],
)
class CustomPasswordResetView(generics.GenericAPIView):
    serializer_class = FinalPasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Лист для скидання паролю надіслано."},
            status=status.HTTP_200_OK,
        )
