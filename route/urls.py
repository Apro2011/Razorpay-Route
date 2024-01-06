from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from route import views

urlpatterns = [
    path("recievers/", views.RecieverList.as_view()),
    path("reciever-details/<int:pk>/", views.RecieverDetails.as_view()),
    path("groups/", views.CreatingGroup.as_view()),
    path("split-payments/<int:pk>/", views.SplitPayments.as_view()),
    path("upipaymentlink/", views.UPIPaymentLinkAPIs.as_view()),
    path("paymentlinkdata/<int:pk>/", views.UPIPaymentLinkData.as_view()),
    path("group-data/<int:pk>/", views.GroupData.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
