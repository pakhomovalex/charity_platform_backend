from django.db import models
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from .models import Category, Project, ProjectImage
from django.db.models import Prefetch

from .serializers import (
    CategorySerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectImageSerializer,
    ProjectCreateSerializer,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_view,
)


@extend_schema_view(
    list=extend_schema(
        summary="Отримати список категорій", tags=["Categories"]
    ),
    retrieve=extend_schema(
        summary="Отримати деталі категорії", tags=["Categories"]
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a project to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Только автор или суперюзер
        return obj.author == request.user or request.user.is_superuser


@extend_schema_view(
    list=extend_schema(
        summary="Отримати список активних проєктів",
        description="Повертає список проєктів зі статусом 'active'. Можна фільтрувати за ID категорії.",
        parameters=[
            OpenApiParameter(
                name="category",
                description="Фільтрувати за ID категорії",
                type=int,
            ),
        ],
        tags=["Projects"],
    ),
    retrieve=extend_schema(
        summary="Отримати деталі проєкту", tags=["Projects"]
    ),
    create=extend_schema(
        summary="Створити новий проєкт",
        description="Створює проєкт, який одразу стає активним. Потрібна аутентифікація.",
        tags=["Projects"],
    ),
    update=extend_schema(summary="Повністю оновити проєкт", tags=["Projects"]),
    partial_update=extend_schema(
        summary="Частково оновити проєкт", tags=["Projects"]
    ),
    destroy=extend_schema(summary="Видалити проєкт", tags=["Projects"]),
)
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for projects.
    - list: list of projects (only active projects)
    - retrieve: detail view of a project
    - create, update, delete: only for project owners
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    parser_classes = [MultiPartParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        print(f"🔥 USER: {user}, ID: {user.id}, AUTH: {user.is_authenticated}")
    
        base_qs = Project.objects.prefetch_related(
            "author", "category"
        ).prefetch_related(
            Prefetch("images", queryset=ProjectImage.objects.order_by("order"))
        )
    
        if not user.is_authenticated:
            return base_qs.filter(status=Project.Status.ACTIVE)
    
        result = base_qs.filter(
            models.Q(status=Project.Status.ACTIVE) | models.Q(author=user)
        ).distinct()
    
        print(f"🔥 QUERYSET COUNT: {result.count()}")
        return result

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        elif self.action == "create":
            return ProjectCreateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        summary="Завантажити зображення в галерею проєкту",
        description="""
Додає одне зображення до галереї конкретного проєкту.
Надсилайте запит у форматі **multipart/form-data** з файлом у полі `image`.
        """,
        tags=["Projects"],
    )
    @action(detail=True, methods=["post"], url_path="upload-image")
    def upload_image(self, request, pk=None):
        project = self.get_object()
        file_obj = request.FILES.get("image")

        if not file_obj:
            return Response(
                {"detail": "Файл з ключем 'image' не знайдено."}, status=400
            )

        project_image = ProjectImage.objects.create(
            project=project, image=file_obj
        )

        serializer = ProjectImageSerializer(
            project_image, context={"request": request}
        )
        return Response(serializer.data, status=201)
