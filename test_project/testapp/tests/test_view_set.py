from django.contrib.auth.models import Group, User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from test_project.testapp.models import UserAccount


class UserAccountTestCase(APITestCase):
    def setUp(self):
        UserAccount.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()

    def test_create_allowed(self):
        admin_group = Group.objects.create(name="admin")
        admin_user = User.objects.create()
        admin_user.groups.add(admin_group)
        self.client.force_authenticate(user=admin_user)

        for name in ["account-mixin-test-list", "account-list"]:
            url = reverse(name)

            response = self.client.post(
                url,
                {"username": "fred", "first_name": "Fred", "last_name": "Rogers"},
                format="json",
            )

            self.assertEqual(response.status_code, 201)

    def test_retrieve_denied(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        banned_group = Group.objects.create(name="banned")
        banned_user = User.objects.create()
        banned_user.groups.add(banned_group)
        self.client.force_authenticate(user=banned_user)

        url = reverse("account-detail", args=[account.id])

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_set_password_should_be_allowed(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        regular_users_group = Group.objects.create(name="regular_users")
        user = User.objects.create()
        user.groups.add(regular_users_group)
        self.client.force_authenticate(user=user)

        url = reverse("account-set-password", args=[account.id])

        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_set_password_should_be_denied(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        user = User.objects.create()
        self.client.force_authenticate(user=user)

        url = reverse("account-set-password", args=[account.id])
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, 403)

    def test_partial_update_should_not_update_status_for_dev_group(self):
        account = UserAccount.objects.create(
            username="fred", first_name="Fred", last_name="Rogers"
        )
        dev_users_group = Group.objects.create(name="dev")
        user = User.objects.create()
        user.groups.add(dev_users_group)
        self.client.force_authenticate(user=user)

        url = reverse("account-detail", args=[account.id])

        response = self.client.patch(
            url, data={"last_name": "Mercury", "status": "inactive"}, format="json"
        )
        self.assertEqual(response.data["last_name"], "Mercury")
        self.assertEqual(response.data["status"], "active")

    def test_partial_update_should_not_update_status_for_account_mario(self):
        account = UserAccount.objects.create(
            username="mario", first_name="Mario", last_name="Rogers"
        )

        dev = Group.objects.create(name="dev")
        user = User.objects.create()
        user.groups.add(dev)
        self.client.force_authenticate(user=user)

        url = reverse("account-detail", args=[account.id])

        response = self.client.patch(
            url, data={"last_name": "Mercury"}, format="json"
        )
        self.assertEqual(response.data["last_name"], "Rogers")

    def test_partial_update_should_not_update_status_for_account_pino(self):
        account = UserAccount.objects.create(
            username="pino", first_name="Mario", last_name="Rogers"
        )

        dev = Group.objects.create(name="dev")
        user = User.objects.create()
        user.groups.add(dev)
        self.client.force_authenticate(user=user)

        url = reverse("account-detail", args=[account.id])

        response = self.client.patch(
            url, data={"last_name": "Mercury"}, format="json"
        )
        self.assertEqual(response.data["last_name"], "Mercury")
