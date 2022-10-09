# Django REST - Access Policy

[![Package version](https://badge.fury.io/py/drf-access-policy.svg)](https://pypi.python.org/pypi/drf-access-policy)
[![Python versions](https://img.shields.io/pypi/status/drf-access-policy.svg)](https://img.shields.io/pypi/status/drf-access-policy.svg/)

This project brings a declaritive, organized approach to managing access control in Django REST Framework projects. Each ViewSet or function-based view can be assigned an explicit policy for the exposed resource(s). No more digging through views or seralizers to understand access logic -- it's all in one place in a format that less technical stakeholders can understand. If you're familiar with other declaritive access models, such as AWS' IAM, the syntax will be familiar.

In short, you can start expressing your access rules like this:

```python
class ArticleAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow"
        },
        {
            "action": ["publish", "unpublish"],
            "principal": ["group:editor"],
            "effect": "allow"
        }
    ]
```

This project has complete test coverage and the base `AccessPolicy` class is only ~150 lines of code: there's no magic here.

Additionally, this project also provides `FieldAccessMixin` that can be added to a serializer to dynamically set fields to `read_only`, based on the access policy. Assign the appropriate access policy class inside the `Meta` declaration. See example below for how this works:

```python
class UserAccountAccessPolicy(AccessPolicy):
    statements = [
        {"principal": "group:admin", "action": ["create", "update"], "effect": "allow"},
        {
            "principal": "group:dev",
            "action": ["update", "partial_update"],
            "effect": "allow",
        },
    ]

    field_permissions = {"read_only": [{"principal": "group:dev", "fields": "status"}]}

class UserAccountSerializer(FieldAccessMixin, serializers.ModelSerializer):
  class Meta:
    model = UserAccount
    fields = ["username", "first_name", "last_name", "status"]
    access_policy = UserAccountAccessPolicy

# Incoming POST/PUT/PATCH request from a user in group:dev...
# serializer = UserAccountSerializer(account, context={'request': request})
# print(serializer.fields["status"].read_only) -> True
```

:warning: **1.0 Breaking Change** :warning:

See [migration notes](https://rsinger86.github.io/drf-access-policy/migration_notes.html) if your policy statements combine multiple conditions into boolean expressions.

---

**Documentation**: <a href="https://rsinger86.github.io/drf-access-policy/" target="_blank">https://rsinger86.github.io/drf-access-policy</a>

**Source Code**: <a href="https://github.com/rsinger86/drf-access-policy" target="_blank">https://github.com/rsinger86/drf-access-policy</a>

---

# Changelog <a id="changelog"></a>

## 1.3 (October 2022)

- Adds `PermittedSlugRelatedField` to re-use `scope_queryset` methods on policies. Thanks @bradydean!

## 1.2 (October 2022)

- Adds `PermittedPkRelatedField` to re-use `scope_queryset` methods on policies.

## 1.1.2 (July 2022)

- Fixes issue with boolean parser and shared request state. Thanks @mari8i!

## 1.1.1 (April 2022)

- Adds support for field-level permissions via a `AccessPolicy.scope_fields(request, fields: dict, instance=None)` method and the `FieldAccessMixin`. Thanks @gianpieropa!

## 1.1.0 (August 2021)

- Adds a mixin for explicitly defining a single access policy per `ViewSet`.

## 1.0.1 (July 2021)

- Fixes race condition between concurrent requests in evaluation of condition expressions. Thanks @goranpavlovic!

## 1.0.0 (July 2021)

- :warning: **Breaking Change** :warning:
  - The `condition` element no longer supports the evaluation of multiple methods joined with boolean logic. These statements must be updated to use the new `condition_expression` element, which _does support_ complex boolean logic.

## 0.9.2 (July 2021)

- Allow defining `reusable_conditions` module as a list. Thanks @HonakerM!

## 0.9.1 (July 2021)

- Fixes attribute error when `request.user` is `None`, which is the case when Django's `AuthenticationMiddleware` is not used. If `request.user` is `None`, the user is anonymous.

## 0.9.0 (April 2021)

- Adds special `admin` and `staff` principal keys to match users with `is_superuser` and `is_staff` set to `True`. Thanks @BarnabasSzabolcs!

## 0.8.7 (February 2021)

- Fixed bug preventing argument being passed to custom condition method if "\*" character used.

## 0.8.6 (January 2021)

- Adds missing requirement to setup.py. Thanks @daviddavis!

## 0.8.5 (January 2021)

- Adds support for boolean expressions in `condition` statement elements. Thanks @tanonl!

## 0.8.1 (October 2020)

- Fixes case where object has no `action_map`. Thanks @oguzhancelikarslan!
- Added missing info to docs. Thanks @hardntrash!

## 0.8.0 (September 2020)

- Workaround for quirk resulting in `action` not always being set. Thanks @oguzhancelikarslan!

## 0.7.0 (August 2020)

- Allows using HTTP method placeholders in `action` element of statements to match request.
  - For example, `"action": ["<method:post>"]` will match all POST requests.

## 0.6.2 (July 2020)

- Uses `user.pk` instead of `user.id` in user principal check, for compatibility with non-`id` primary keys.
- Fixes to documentation. Thanks @oguzhancelikarslan!

## 0.6.1 (June 2020)

- Replaces references to "delete" action with "destroy" in docs/tests, to be consistent with DRF's ViewSet actions. Thanks @greenled!

## 0.6.0 (May 2020)

- Only call database-hitting `get_user_group_values` if needed in private method. Thanks KillianMeersman!
- Use `prefetch_related_objects` to ensure that user's groups aren't fetched more than once. Thanks filwaline!

## 0.5.1 (December 2019)

- Tox config updates and typo fixes in docs.

## 0.5.0 (September 2019)

- Add option to define re-usable custom conditions/permissions in a module that can be referenced by multiple policies.

## 0.4.2 (June 2019)

- Fixes readme format for Pypy display.

## 0.4.0 (June 2019)

- Allow passing arguments to condition methods, via condition values formatted as `{method_name}:{arg_value}`.

## 0.3.0 (May 2019)

- Adds special `<safe_methods>` action key that matches when the current request is an HTTP read-only method: HEAD, GET, OPTIONS.

## 0.2.0 (May 2019)

- Adds special `authenticated` and `anonymous` principal keys to match any authenticated user and any non-authenticated user, respectively. Thanks @bogdandm for discussion/advice!

## 0.1.0 (May 2019)

- Initial release

# Testing

Tests are found in a simplified Django project in the `/tests` folder. Install the project requirements and do `./manage.py test` to run them.

# License

See [License](LICENSE.md).
