from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from route import views

urlpatterns = [
    path("recievers/", views.RecieverList.as_view()),
    path("split-payments/", views.SplitPayments.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
