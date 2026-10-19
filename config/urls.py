from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from core import api

router = DefaultRouter()
for key, vs in api.VIEWSETS.items():
    router.register(key, vs, basename=key)

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/auth/login/", api.LoginView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/me/", api.me),
    path("api/health/", api.health),
    path("api/meta/", api.meta_index),
    path("api/meta/<str:key>/", api.meta_resource),
    path("api/dashboard/", api.dashboard),
    path("api/control-tower/", api.control_tower),
    path("api/", include(router.urls)),
    re_path(r"^(?!api/|static/|django-admin/).*$", TemplateView.as_view(template_name="index.html")),
]
