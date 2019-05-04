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
        },
    ]
```

This project has complete test coverage and the base `AccessPolicy` class is only ~150 lines of code. There's no magic here. You can probably understand how it works by reading the source code for 15 minutes.

# Table of Contents:

- [Installation](#installation)
- [Example #1: Policy for ViewSet](#example-1-an-article-viewset)
- [Example #2: Policy for Function-Based View](#example-2-function-based-views)
- [Documentation](#documentation)
  * [Statement Elements](#statement-elements)
  * [Policy Evaluation Logic](#policy-evaluation-logic)
  * [Object-Level Permissions/Conditions](#object-level-perm)
  * [Multitenancy Data/Restricting QuerySets](#multitenancy-data--restricting-querysets)
  * [Attaching to ViewSets and Function-Based Views](#attaching-to-viewsets-and-function-based-views)
  * [Loading Statements from External Source](#loading-statements-from-external-source)
  * [Customizing User Group/Role Values](#customizing-user-grouprole-values)
  * [Customizing Principal Prefixes](#customizing-principal-prefixes)
- [Changelog](#changelog)
- [Testing](#testing)
- [License](#license)

# Setup

```
pip install drf-access-policy
```

To define a policy, import `AccessPolicy` and subclass it:

```python
from rest_access_policy import AccessPolicy


class ShoppingCartAccessPolicy(AccessPolicy):
    statements = [] # Now read on...
```

# Example #1: Policy for ViewSet

In a nutshell, a policy is comprised of "statements" that declare what "actions" a "principal" can or cannot perform on the resource, with optional custom checks that can examine any detail of the current request.

Here are two more key points to remember going forward:
* all access is implicitly denied by default
* any statement with the "deny" effect overrides any and all "allow" statement

Now let's look at the policy below an articles endpoint, provided through a view set.

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
    permission_classes = (ArticleAccessPolicy, )

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

# Example #2: Policy for Function-Based View

You can also you policies with function-based views. The action to reference in your policy statements is the name of the function. You can also bundle multiple functions into the same policy as the example below shows.

```python
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

| Name           |  Description                         |   Examples    |
| -------------- |-------------------------------------:|--------------:|
| principal     | Identifies the user of the current request by the name of a group they belong to or their user id. Can be formatted as a string or list of strings. Use an asterisk ("*") if you want the statement to apply to all principals. | `["group:admins"]` <br> `["id:5352"]`    |
| action     | The action or actions that the statement applies to. Can be formatted as a string or list of strings. The value should match the name of a view set method or the name of the view function. Use an asterisk ("*") if you want the statement to apply to all actions. | `["list", "delete", "create]` <br> `["*"]`    |
| effect     | Whether the statement, if it is in effect, should allow or deny access. All access is denied by default, so use `deny` when you'd like to override an `allow` statement that will also be in effect. Should be a string equal to either `deny` or `allow`. | `"allow"` <br> `"deny"`    |
| condition     | The name of a method on the policy that returns a boolean. The method signature is `condition(request, view, action: str)`. If true, the policy will be in effect. Useful for enforcing object-level permissions. If list of strings, all conditions must evaluate to `True`. | `"is_manager_for_account"` <br> `"is_author_of_post"` <br> `["balance_is_positive", "account_is_not_frozen"]`   |

## Policy Evaluation Logic

To determine whether access to a request is granted, all applicable statements are first filtered. A statement is applicable to the current request if all of the following are true (1) the request user matches one of the statement's principals, (2) the name of the method/function matches one of its actions, and (3) any custom conditions evaluate to true.

The request is allowed if any of the statements have an effect of "allow", and none have an effect of "deny". By default, all requests are denied.

## Object-Level Permissions/Conditions <a id="object-level-perm"> </a>

You may be wondering, but what object-level permissions? Not to worry - you can easily check object-level access in a custom condition that's evaluated to determine whether the statement takes effect. This condition is passed the `view` instance, so you can easily get the model instance with a call to `view.get_object()`. You can even reference multiple conditions, to keep your access methods focused and easy to test.

```python
class AccountAccessPolicy(AccessPolicy):
    statements = [
        ## ... other statements ...
        {
            "action": ["withdraw"],
            "principal": ["*"],
            "effect": "allow",
            "condition": ["balance_is_positive", "is_account_owner"]     
        }
        ## ... other statements ...
    ]

    def balance_is_positive(self, request, view, action) -> bool:
        account = view.get_object()
        return account.balance > 0

    def is_account_owner(self, request, view, action) -> bool:
        account = view.get_object()
        return account.owner == request.user
```
## Multitenancy Data / Restricting QuerySets

You can define a class method on your policy class that takes a QuerySet and the current request and returns a securely scoped QuerySet representing only the database rows that the current user should have access to. This is helpful for multitenant situations or more generally when users should not have full visibility to model instances. Of course you could do this elsewhere in your code, but putting this method on the policy class keeps all access logic in a single place.

```python
    class PhotoAlbumAccessPolicy(AccessPolicy):
        # ... statements, etc ...

        # Users can only access albums they have created
        @classmethod
        def scope_queryset(cls, request, qs):
            return qs.filter(creator=request.user)


    class TodoListAccessPolicy(AccessPolicy):
        # ... statements, etc ...

        # Users can only access todo lists owned by their organization
        @classmethod
        def scope_queryset(cls, request, qs):
            user_orgs = request.user.organizations.all()
            return qs.filter(org__id__in=user_orgs)
```

## Attaching to ViewSets and Function-Based Views

You attach access policies the same way you do with regular DRF permissions.

For ViewSets, add it to `permissions` property:
```python
class ArticleViewSet(ModelViewSet):
    permission_classes = (ArticleAccessPolicy, )
```

For function-based views, add it to `permissions_classes` decorator:
```python
@api_view(["GET"])
@permission_classes((ArticleAccessPolicy,))
def create_article(request):
    ## you logic here...
    pass
```

## Loading Statements from External Source

If you don't want your policy statements hardcoded into the classes, you can load them from an external data source: a great step to take because you can then change access rules without redeploying code. 

Just define a method on your policy class called `get_policy_statements`, which has the following signature:
`get_policy_statements(self, request, view) -> List[dict]`

Example:

```python
class UserAccessPolicy(AccessPolicy):
    id = 'user-policy'

    def get_policy_statements(self, request, view) -> List[dict]:
        statements = data_api.load_json(self.id)
        return json.loads(statements)
```

You probably want to only define this method once on your own custom subclass of `AccessPolicy`, from which all your other access policies inherit.

## Customizing User Group/Role Values

If you aren't using Django's built-in auth app, you may need to define a custom way to retrieve the role/group names to which the user belongs. Just define a method called `get_user_group_values` on your policy class. It is passed a single argument: the  user of the current request. In the example below, the user model has a to-many relationship with a "roles", which have their "name" value in a field called "title".

```python
class UserAccessPolicy(AccessPolicy):
    # ... other properties and methods ...

    def get_user_group_values(self, user) -> List[str]:
        return list(user.roles.values_list("title", flat=True))
```
## Customizing Principal Prefixes

By default, the prefixes to identify the type of principle (user or group) are "id:" and "group:", respectively. You can customize this by setting these properties on your policy class:

```python
class FriendRequestPolicy(permissions.BasePermission):
    group_prefix = "role:"
    id_prefix = "staff_id:"

    # .. the rest of you policy definition ..
```

# Changelog <a id="changelog"></a>

TODO

# Testing

Tests are found in a simplified Django project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
