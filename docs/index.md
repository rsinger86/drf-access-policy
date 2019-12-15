# Django REST - Access Policy

[![Package version](https://badge.fury.io/py/drf-access-policy.svg)](https://pypi.python.org/pypi/drf-access-policy)
[![Python versions](https://img.shields.io/pypi/status/drf-access-policy.svg)](https://img.shields.io/pypi/status/drf-access-policy.svg/)

This project brings a declaritive, organized approach to managing access control in Django REST Framework projects. Each `ViewSet` or function-based view can be assigned an explicit policy for the exposed resource(s). No more digging through views or seralizers to understand access logic -- it's all in one place in a format that less technical stakeholders can understand. If you're familiar with other declaritive access models, such as AWS' IAM, the syntax will be familiar. 

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
Key Features:

  * A declarative JSON syntax makes access rules easy to understand, reducing the chance of accidental exposure
  * The [option](/loading_external_source) to load access statements from an external source means non-programmers can edit access policies without redeployments
  * Write [plain Python methods that examine every facet](/object_level_permissions) of the current request (user, data, model instance) for more granular, contextual access rules
  * Keep all your access logic in one place: add `scope_queryset` methods to access policy classes to [apply filtering for multitenant databases](/multi_tenacy)

This project has complete test coverage and the base `AccessPolicy` class is only ~150 lines of code: there's no magic here.

## Requirements

Python 3.5+

## Installation
```
pip install drf-access-policy
```

## Quick Example
To define a policy, import `AccessPolicy` and subclass it:

```python
from rest_framework.viewsets import ModelViewSet
from rest_access_policy import AccessPolicy


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


class ArticleViewSet(ModelViewSet):
    permission_classes = (ArticleAccessPolicy, )
```

[Read on](usage/view_set_usage) for a full example of how to add an access policy to a `ViewSet`.