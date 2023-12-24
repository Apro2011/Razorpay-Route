from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from sender_auth_app import views

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
    path("login/", views.SenderAuthAPI.as_view()),
]
