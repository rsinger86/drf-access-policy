# Django REST - Access Policy

[![Package version](https://badge.fury.io/py/drf-access-policy.svg)](https://pypi.python.org/pypi/drf-access-policy)
[![Python versions](https://img.shields.io/pypi/status/drf-access-policy.svg)](https://img.shields.io/pypi/status/drf-access-policy.svg/)


# About

This project brings a declaritive, organized approach to managing access control in Django REST projects. Each ViewSet or function-based view can be assigned an explicit policy for the exposed resource(s). No more digging through views or seralizers to understand authorization logic -- it's all in one place, in a format that less technical stakeholders can understand. If you're familiar with other declaritive authorization models, such as AWS' IAM, the syntax will be immediately familiar. 

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
        },
    ]
```

# Table of Contents:

- [Installation](#installation)
- [Getting Started: An Example](#features)
- [Scoping User/Tenant QuerySets](#features)
- [Custom Context Conditions](#features)
- [Helpful Conventions](#features)
- [Folder Structure](#features)
- [Documentation](#docs)
- [Statement Elements](#docs)
- [Designating the Principal](#docs)
- [Loading in Policy Statements](#docs)
- [Changelog](#changelog)
- [Testing](#testing)
- [License](#license)

# Installation

```
pip install drf-access-policy
```

# Example #1: An "Article" ViewSet

In a nutshell, a policy is comprised of "statements" that declare what "actions" a "principal" can or cannot perform on the resource, with optional custom checks that can examine any detail of the current request.

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
            "action": ["delete"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "is_author"         
        },
        {
            "action": ["*"],
            "principal": ["*"],
            "effect": "deny",
            "condition": "is_happy_hour"
        }
    ]

    def is_author(self, request, view, action) -> bool:
        article = view.get_object()
        return request.user == article.author 

    def is_happy_hour(self, request, view, action) -> bool:
        now = datetime.datetime.now()
        return now.hour >= 17 and now.hour <= 18:

    @classmethod
    def scope_queryset(cls, request, queryset):
        if request.user.groups.filter(name='editor').exists():
            return queryset

        return queryset.filter(status='published')


class ArticleViewSet(ModelViewSet):
    # Just stick the policy here, as you would do with
    # regular DRF "permissions"
    permissions = (ArticleAccessPolicy, )

    # Helper property here to make get_queryset logic
    # more explicit
    @property
    def access_policy(self):
        return self.permission_classes[0]

    # Ensure that current user can only see the models 
    # they are allowed to see
    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, Articles.objects.all()
        )
    
    @action(method="POST")
    def publish(self, request, *args, **kwargs):
        pass

    @action(method="POST")
    def unpublish(self, request, *args, **kwargs):
        pass

    # the rest of you view set definition...
```

The actions correspond to the names of methods on the ViewSet. 

In the example above, the following rules are put in place:
- anyone is allowed to list and retrieve articles
- users in the editor group are allowed to publish and unpublish articles
- in order to delete an article, the user must be the author of the article. Notice how the condition method `is_author` calls `get_object()` on the view to get the current article.
- if the condition `is_happy_hour`, evaluates to `True`, then no one is allowed to do anything.

Additionally, we have some logic in the `scope_queryset` method for filtering which models are visible to the current user. Here, we want users to only see published articles, unless they are an editor, in which case they case see articles with any status. You have to remember to call this method from the view, so I'd suggest reviewing this as part of a security audit checklist.

# Example #2: Function-Based Views

You can also you policies with function-based views. The action to reference in your policy statements is the name of the function. You can also bundle multiple functions into the same policy as the example below shows.

```python
from rest_access_policy import AccessPolicy


class AuditLogsAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["search_logs"],
            "principal": "group:it_staff",
            "effect": "allow"
        },
        {
            "action": ["download_logs"],
            "principal": ["group:it_admin"],
            "effect": "allow"            
        }
    ]


@api_view(["GET"])
@permission_classes((AuditLogsAccessPolicy,))
def search_logs(request):
    ## you logic here...
    pass


@api_view(["GET"])
@permission_classes((AuditLogsAccessPolicy,))
def download_logs(request):
    ## you logic here...
    pass


```

# Documentation 

## Statement Elements

## Specifying the Principal

## Loading Statements from External Source

# Changelog <a id="changelog"></a>

TODO

# Testing

Tests are found in a simplified Django project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
