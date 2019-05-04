from django.conf.urls import include, url
from rest_framework import routers
from test_project.testapp.views import UserAccountViewSet, delete_logs, get_logs

# Standard viewsets
router = routers.DefaultRouter()
router.register(r"accounts", UserAccountViewSet, base_name="account")

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^delete-logs/", delete_logs, name="delete-logs"),
    url(r"^get-logs/", get_logs, name="get-logs"),
]
