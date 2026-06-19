from rest_framework import serializers
from django.contrib.auth import get_user_model
from projects.serializers import (
    CategorySerializer,
    ProjectForAuthorPageSerializer,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string

User = get_user_model()


class AuthorListSerializer(serializers.ModelSerializer):
    specialization = CategorySerializer(many=True, read_only=True)
    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "avatar",
            "city",
            "specialization",
            "project_count",
            "date_joined",
            "date_joined",
            "telegram_url",
            "instagram_url",
            "facebook_url",
        ]


class AuthorDetailSerializer(serializers.ModelSerializer):
    specialization = CategorySerializer(many=True, read_only=True)
    project_count = serializers.IntegerField(read_only=True)
    projects = ProjectForAuthorPageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "avatar",
            "bio",
            "city",
            "specialization",
            "phone_number",
            "telegram_url",
            "instagram_url",
            "facebook_url",
            "date_joined",
            "project_count",
            "projects",
        ]


class CurrentUserSerializer(serializers.ModelSerializer):
    specialization = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "bio",
            "city",
            "specialization",
            "phone_number",
            "telegram_url",
            "instagram_url",
            "facebook_url",
            "is_superuser"
        ]
        read_only_fields = ["id", "email"]


class CustomRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ("email", "password", "password2")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }

    def validate(self, attrs):
        if attrs.get("password") != attrs.pop("password2", None):
            raise serializers.ValidationError(
                {"password": "Паролі не співпадають."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_staff=True,
        )
        return user


class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["avatar"]


class FinalPasswordResetSerializer(serializers.Serializer):
    """
    Повністю кастомний серіалізатор, який сам знаходить користувача,
    генерує токени і відправляє лист, ігноруючи логіку dj-rest-auth.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        # Перевіряємо, чи існує активний користувач з таким email
        try:
            self.user = User.objects.get(email__iexact=value, is_active=True)
        except User.DoesNotExist:
            # Не видаємо помилку, щоб не розкривати, які email зареєстровані
            pass
        return value

    def save(self):
        request = self.context.get('request')
        
        # Перевіряємо, чи був знайдений користувач на етапі валідації
        if not hasattr(self, 'user'):
            # Якщо користувач не знайдений, нічого не робимо (тиха відмова)
            return

        user = self.user
        
        # 1. Готуємо контекст для email-шаблону
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        url_template = settings.PASSWORD_RESET_URL_TEMPLATE
        password_reset_url = url_template.format(uid=uid, token=token)
        
        context = {
            'user': user,
            'password_reset_url': password_reset_url,
        }

        # 2. Рендеримо тему та тіло листа з наших шаблонів
        subject = render_to_string('account/email/password_reset_key_subject.txt', context)
        subject = ''.join(subject.splitlines()) # Прибираємо переноси рядків з теми

        body = render_to_string('account/email/password_reset_key_message.txt', context)

        # 3. Відправляємо лист, використовуючи базову функцію Django
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[user.email],
            fail_silently=False,
        )