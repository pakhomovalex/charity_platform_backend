from django.contrib import admin
from .models import Category, Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image",)
    verbose_name = "Зображення"
    verbose_name_plural = "Галерея проєкту"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectImageInline]
    list_display = (
        "title",
        "author",
        "status",
        "category",
        "created_at",
        "end_date",
    )
    list_filter = ("status", "category", "donation_type")
    search_fields = ("title", "author__username", "description")
    readonly_fields = ("created_at", "updated_at", "views_count")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        fields = list(super().get_fields(request, obj))
        if "author" in fields:
            fields.remove("author")
        return fields


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    # def has_add_permission(self, request):
    #     return request.user.is_superuser

    # def has_change_permission(self, request, obj=None):
    #     return request.user.is_superuser

    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser
