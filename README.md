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

---

**Documentation**: <a href="https://rsinger86.github.io/drf-access-policy/" target="_blank">https://rsinger86.github.io/drf-access-policy</a>

**Source Code**: <a href="https://github.com/rsinger86/drf-access-policy" target="_blank">https://github.com/rsinger86/drf-access-policy</a>

---

# Changelog <a id="changelog"></a>

## 0.8.5 (January 2021)
* Adds support for boolean expressions in `condition` statement elements. Thanks @tanonl!

## 0.8.1 (October 2020)
* Fixes case where object has no `action_map`. Thanks @oguzhancelikarslan!
* Added missing info to docs. Thanks @hardntrash!

## 0.8.0 (September 2020)
* Workaround for quirk resulting in `action` not always being set. Thanks @oguzhancelikarslan!

## 0.7.0 (August 2020)
* Allows using HTTP method placeholders in `action` element of statements to match request.
  * For example, `"action": ["<method:post>"]` will match all POST requests. 

## 0.6.2 (July 2020)
* Uses `user.pk` instead of `user.id` in user principal check, for compatibility with non-`id` primary keys.
* Fixes to documentation. Thanks @oguzhancelikarslan!

## 0.6.1 (June 2020)
* Replaces references to "delete" action with "destroy" in docs/tests, to be consistent with DRF's ViewSet actions. Thanks @greenled!

## 0.6.0 (May 2020)
* Only call database-hitting `get_user_group_values` if needed in private method. Thanks KillianMeersman!
* Use `prefetch_related_objects` to ensure that user's groups aren't fetched more than once. Thanks filwaline!

## 0.5.1 (December 2019)
* Tox config updates and typo fixes in docs.

## 0.5.0 (September 2019)
* Add option to define re-usable custom conditions/permissions in a module that can be referenced by multiple policies.

## 0.4.2 (June 2019)
* Fixes readme format for Pypy display.

## 0.4.0 (June 2019)
* Allow passing arguments to condition methods, via condition values formatted as `{method_name}:{arg_value}`.

## 0.3.0 (May 2019)
* Adds special `<safe_methods>` action key that matches when the current request is an HTTP read-only method: HEAD, GET, OPTIONS.

## 0.2.0 (May 2019)
* Adds special `authenticated` and `anonymous` principal keys to match any authenticated user and any non-authenticated user, respectively. Thanks @bogdandm for discussion/advice!

## 0.1.0 (May 2019)
* Initial release

# Testing

Tests are found in a simplified Django project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
