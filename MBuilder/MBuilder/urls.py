from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import signup_view
from accounts.views import profile_view
from accounts.views import custom_logout

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", include("main.urls")),
        path("accounts/", include("django.contrib.auth.urls")),
        path("accounts/signup/", signup_view, name="signup"),
        path("accounts/profile/", profile_view, name="profile"),
        path("logout/", custom_logout, name="logout"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
