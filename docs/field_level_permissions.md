# Field-Level Permissions

Often, depending on the user, not all fields should be visible or only a subset should be writable.

For these scenarios, you can define a `scope_fields` method on the access policy which is passed the `dict` of `name:Field` pairs from a serializer used with the `FieldAccessMixin`.

## Scenario: A field should only exist for admin users

Requirement: When a customer account is serialized or deserialized, the `email` field should only be present if the user is an admin.

You could define a `scope_fields` method on the access policy like this:

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

Make sure to add the `FieldAccessMixin` to your serializer and assign it the correct access policy in its `Meta` class:

```python
from rest_access_policy import FieldAccessMixin


class CustomerAccountSerializer(FieldAccessMixin, serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ["username", "first_name", "last_name", "email"]
        access_policy = CustomerAccountAccessPolicy
```

## Scenario: A field should be read-only, except for the author

Requirement: When a request is made to update an article, the `content` field should be read-only, except for the author.

You could define a `scope_fields` method on the access policy like this:

```python
class CustomerAccountAccessPolicy(AccessPolicy):
    statements = [
      # statements that define who is allowed to perform what action
    ]

    @classmethod
    def scope_fields(cls, request, fields: dict, instance=None) -> dict:
        if instance and instance.author != request.user:
            fields["content"].read_only = True
        return fields
```

As before, make sure to add the `FieldAccessMixin` to your serializer and assign it the correct access policy in its `Meta` class.
