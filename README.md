# Django REST - Access Policy

[![Package version](https://badge.fury.io/py/drf-access-policy.svg)](https://pypi.python.org/pypi/drf-access-policy)
[![Python versions](https://img.shields.io/pypi/status/drf-access-policy.svg)](https://img.shields.io/pypi/status/drf-access-policy.svg/)

# Overview

This project brings a declaritive, organized approach to managing access control in Django REST projects. Each ViewSet or function-based view can be assigned an explicit policy that centralizes access rules for the exposed resource or resources. If you've worked with AWS' Identity and Access Managment policies, the syntax will be immediately familiar. If not, a "policy" is comprised of "statements" that declare what "actions" a "principal" can perform on the resource, with optional custom checks that can examine any detail of the current request.

See the example below for how you can define access to your articles endpoint.

```python
from rest_access_policy import AccessPolicy


class ArticleAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow"
        },
        {
            "action": ["*"],
            "principal": ["group:super_admin'],
            "effect": "allow"
        },
        {
            "action": ["publish", "unpublish"],
            "principal": ["group:editor'],
            "effect": "allow"            
        },
        {
            "action": ["*"],
            "principal": ["*"],
            "effect": "deny",
            "custom_context_condition": "is_happy_hour"
        }
    ]

    def is_happy_hour(self, request, view, action) -> bool:
        if request.user.username === "Fred": # It's always happy hour for this guy ... so he never gets access.
            return True
    
        now = datetime.datetime.now()
        return now.hour >= 17 and now.hour <= 18:



class ArticleViewSet(ModelViewSet):
    permissions = (ArticleAccessPolicy, )
    # the rest of you view set definition...

    @action(method="POST")
    def publish(self, request, *args, **kwargs):
        pass

    @action(method="POST")
    def unpublish(self, request, *args, **kwargs):
        pass
```

In the example above, the following rules are put in place:
- anyone is allowed to list and retrieve articles
- users in the super_admin group are allowed to do anything to articles
- users in the editor group are allowed publish and unpublish articles
- if the `custom_context_condition`, `is_happy_hour`, evaluates to `True`, then no one is allowed to do anything with articles.

# Table of Contents:

- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Examples](#examples)
- [Documentation](#docs)
- [Changelog](#changelog)
- [Testing](#testing)
- [License](#license)

# Installation

```
pip install drf-access-policy
```

# Requirements

* Python >= 3.4
* Django >= 1.8

# Usage 

Either extend the provided abstract base model class:

```python
from django_lifecycle import LifecycleModel, hook


class YourModel(LifecycleModel):
    name = models.CharField(max_length=50)

```
# Changelog <a id="changelog"></a>

TODO

# Testing

Tests are found in a simplified Django project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
