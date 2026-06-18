from rest_framework import serializers
from .models import Category, Project, ProjectImage
from users.models import CustomUser
from drf_spectacular.utils import extend_schema_field


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "bio",
            "avatar",
            "full_name",
            "telegram_url",
            "instagram_url",
            "facebook_url",
        ]


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "image", "order"]

class ProjectCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания проекта с загрузкой изображений"""
    
    class Meta:
        model = Project
        fields = [
            "title",
            "subtitle",
            "description",
            "category",
            "donation_type",
            "price",
            "target_amount",
            "donation_percentage",
            "fundraising_goal",
            "end_date",
            "monobank_jar_url",
            "privatbank_konvert_url",
            "paypal_me_url",
            "other_payment_details",
            "status",
        ]

    def create(self, validated_data):
        validated_data['status'] = 'active'

        request = self.context.get('request')
        images = request.FILES.getlist('images') if request else []
        
        # Создаём проект
        project = Project.objects.create(**validated_data)
        
        # Создаём изображения
        for index, image in enumerate(images):
            ProjectImage.objects.create(
                project=project,
                image=image,
                order=index
            )
        
        return project


class ProjectListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "subtitle",
            "author",
            "category",
            "donation_type",
            "cover_image",
            "status",
            "end_date",
            "donation_type",
            "price",
            "donation_percentage",
            "target_amount",
        ]

    @extend_schema_field(serializers.URLField())
    def get_cover_image(self, obj):
        first_image = obj.images.first()

        if first_image and first_image.image:
            request = self.context.get("request")
            return request.build_absolute_uri(first_image.image.url)

        return None


class ProjectDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "subtitle",
            "author",
            "category",
            "images",
            "description",
            "fundraising_goal",
            "target_amount",
            "donation_type",
            "price",
            "donation_percentage",
            "monobank_jar_url",
            "privatbank_konvert_url",
            "paypal_me_url",
            "other_payment_details",
            "status",
            "created_at",
            "end_date",
            "views_count",
        ]


class ProjectForAuthorPageSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "subtitle",
            "category",
            "cover_image",
            "donation_type",
            "status",
            "end_date",
            "donation_type",
            "price",
            "donation_percentage",
            "target_amount",
        ]

    @extend_schema_field(serializers.URLField())
    def get_cover_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get("request")
            return request.build_absolute_uri(first_image.image.url)
        return None
