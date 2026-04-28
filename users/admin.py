from django.contrib import admin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    list_filter = ("is_staff", "is_active")

    def get_fieldsets(self, request, obj=None):

        if obj:
            if request.user.is_superuser:
                return (
                    (
                        "Основна інформація",
                        {
                            "fields": (
                                "email",
                                "first_name",
                                "last_name",
                                "username",
                                "avatar",
                            )
                        },
                    ),
                    (
                        "Додаткова інформація",
                        {"fields": ("bio", "city", "specialization")},
                    ),
                    (
                        "Контакти",
                        {
                            "fields": (
                                "phone_number",
                                "telegram_url",
                                "instagram_url",
                                "facebook_url",
                            )
                        },
                    ),
                    (
                        "Права доступу",
                        {
                            "fields": (
                                "is_active",
                                "is_staff",
                                "is_superuser",
                                "groups",
                            )
                        },
                    ),
                    ("Важливі дати", {"fields": ("last_login", "date_joined")}),
                )
            else:
                return (
                    (
                        "Персональна інформація",
                        {
                            "fields": (
                                "first_name",
                                "last_name",
                                "bio",
                                "city",
                                "avatar",
                            )
                        },
                    ),
                    (
                        "Контакти",
                        {
                            "fields": (
                                "phone_number",
                                "telegram_url",
                                "instagram_url",
                                "facebook_url",
                            )
                        },
                    ),
                    ("Спеціалізація", {"fields": ("specialization",)}),
                )

        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):

        if not obj:
            return self.add_form
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data["password1"])

        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(pk=request.user.pk)
