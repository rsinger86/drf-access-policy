from django.urls import include, re_path
from rest_framework import routers
from test_project.testapp.views import (
    UserAccountViewSet,
    UserAccountViewSetWithMixin,
    delete_logs,
    get_logs,
    get_landing_page,
)

# Standard viewsets
router = routers.DefaultRouter()
router.register(r"accounts", UserAccountViewSet, basename="account")
router.register(r"accounts-mixin-test", UserAccountViewSetWithMixin, basename="account-mixin-test")


urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^delete-logs/", delete_logs, name="delete-logs"),
    re_path(r"^get-logs/", get_logs, name="get-logs"),
    re_path(r"^get-landing-page/", get_landing_page, name="get-landing-page"),
]
