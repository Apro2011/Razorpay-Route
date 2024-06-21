from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from sender_auth_app import views
from django.conf.urls.static import static
from core import settings
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path(
        "api/token/",
        jwt_views.TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("sender/", views.SenderCreationAPI.as_view()),
    path("sender-details/", views.SenderDetailsAPI.as_view()),
    path("login/", views.SenderAuthAPI.as_view()),
    path("logout/", views.SenderLogoutView.as_view(), name="auth_logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = format_suffix_patterns(urlpatterns)
