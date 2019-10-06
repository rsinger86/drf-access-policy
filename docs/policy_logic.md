# Policy Evaluation Logic

To determine whether access to a request is granted, two steps are applied: (1) *filtering statements*, to find out which statements apply to the request (2) *denying or allowing* the request based on those statements.

1. *Filtering statements*: A statement is applicable to the current request if all of the following are true (a) the request user matches one of the statement's principals, (b) the name of the method/function matches one of its actions, and (c) all custom conditions evaluate to true.
2. *Allow or deny*: The request is allowed if any of the statements have an effect of "allow", and none have an effect of "deny". By default, all requests are denied. Requests are implicitly denied if no `Allow` statements are found, and they are explicitly denied if any `Deny` statements are found. `Deny` statements *trump* `Allow` statements.

## Example
Consider the following access policy and `ViewSet`.

```python
class ArticleAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow"
        },
        {
            "action": ["publish"],
            "principal": ["group:editor"],
            "effect": "allow"            
        }
    ]


class ArticleViewSet(ModelViewSet):
    permission_classes = (ArticleAccessPolicy, )

    @action(method="POST")
    def publish(self, request, *args, **kwargs):
        pass
```

A user in the group `sales` is allowed to `list` and `retrieve` articles because of the first statement. They cannot `publish` because all access is implicitly denied, however uses in the group `editor` can `publish` due to the second statement.