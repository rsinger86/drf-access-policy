from django.conf.urls import include, url
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
    url(r"^", include(router.urls)),
    url(r"^delete-logs/", delete_logs, name="delete-logs"),
    url(r"^get-logs/", get_logs, name="get-logs"),
    url(r"^get-landing-page/", get_landing_page, name="get-landing-page"),
]
