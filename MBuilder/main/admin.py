from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from accounts.models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Настройки для списка пользователей
    list_display = ("email", "first_name", "is_staff", "is_active", "avatar_preview")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name")
    ordering = ("email",)

    # Поля для редактирования пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("first_name", "avatar", "avatar_preview")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    # Поля для создания пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "password1", "password2"),
            },
        ),
    )

    # Отображение аватара
    readonly_fields = ("avatar_preview",)

    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="100" style="border-radius: 50%;" />'
            )
        return "Аватар не выбран"

    avatar_preview.short_description = "Превью аватара"


admin.site.register(CustomUser, CustomUserAdmin)
