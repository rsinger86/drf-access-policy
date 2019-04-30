# Django REST - Access Policy

[![Package version](https://badge.fury.io/py/drf-access-policy.svg)](https://pypi.python.org/pypi/drf-access-policy)
[![Python versions](https://img.shields.io/pypi/status/drf-access-policy.svg)](https://img.shields.io/pypi/status/drf-access-policy.svg/)

# Table of Contents:

- [Overview](#overview)
- [Installation](#installation)
- [Requirements](#requirements)
- [Examples](#features)
- [Scoping User/Tenant QuerySets](#features)
- [Custom Context Conditions](#features)
- [Helpful Conventions](#features)
- [Folder Structure](#features)
- [ViewSet Property](#features)
- [Documentation](#docs)
- [Statement Elements](#docs)
- [Designating the Principal](#docs)
- [Loading in Policy Statements](#docs)
- [Changelog](#changelog)
- [Testing](#testing)
- [License](#license)

# Overview

This project brings a declaritive, organized approach to managing access control in Django REST projects. Each ViewSet or function-based view can be assigned an explicit policy that centralizes access rules for the exposed resource or resources.

If you've worked with AWS' Identity and Access Managment policies, the syntax will be immediately familiar. In a nutshell, a policy is comprised of "statements" that declare what "actions" a "principal" can perform on the resource, with optional custom checks that can examine any detail of the current request. Let's look at an example to unpack that!

Here are two more key points to remember going forward:
* all access is implicitly denied by default
* any statement with the "deny" effect overrides any and all "allow" statement

Now let's look at the policy below an articles endpoint, provided through a view set.

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
            "action": ["publish", "unpublish"],
            "principal": ["group:editor"],
            "effect": "allow"            
        },
        {
            "action": ["*"],
            "principal": ["*"],
            "effect": "deny",
            "condition": "is_happy_hour"
        }
    ]

    def is_happy_hour(self, request, view, action) -> bool:
        # It's always happy hour for this guy ... so he never gets access.
        if request.user.username === "Fred": 
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
- users in the editor group are allowed to publish and unpublish articles
- if the condition `is_happy_hour`, evaluates to `True`, then no one is allowed to do anything

# Installation

```
pip install drf-access-policy
```

# Getting Started 

Either extend the provided abstract base model class:

```python
from django_lifecycle import LifecycleModel, hook


class YourModel(LifecycleModel):
    name = models.CharField(max_length=50)

```

# Examples



# Documentation 

## Statement Elements

# Changelog <a id="changelog"></a>

TODO

# Testing

Tests are found in a simplified Django project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
