# Field-Level Permissions

Often, depending on the user, not all fields should be visible or only a subset should be writable. For example, in a SaaS app maybe only admin users can view the email field of customer accounts.

For these scenarios, you can define a `scope_fields` method on the access policy which is passed the `dict` of `name:Field` pairs from the serializer definition.

```python
class CustomerAccountAccessPolicy(AccessPolicy):
    statements = [
      # statements that define who is allowed to perform what action
    ]

    @classmethod
    def scope_fields(cls, request, fields: dict, instance=None) -> dict:
        if not request.user.is_admin():
            fields.pop('email', None)
        return fields
```

Then, add the `FieldAccessMixin` to your serializer and assign it the correct access policy in its `Meta` class:

```python
from rest_access_policy import FieldAccessMixin


class CustomerAccountSerializer(FieldAccessMixin, serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ["username", "first_name", "last_name", "email"]
        access_policy = CustomerAccountAccessPolicy
```

When a customer account is serialized or deserialized, the `email` field will only be present if the user is an admin.
