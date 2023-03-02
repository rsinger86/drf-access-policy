# Statement Dataclass

A `Statement` dataclass can be used instead of dictionaries to define policy statements.

For example, the following policies are equivalent:

```python
from rest_access_policy import Statement


class ArticleAccessPolicy(AccessPolicy):
    statements = [
        Statement(
            action="destroy", 
            principal=["*"], 
            effect="allow", 
            condition="is_author"
        )
    ] 

    def is_author(self, request, view, action) -> bool:
        article = view.get_object()
        return request.user == article.author



class ArticleAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["destroy"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "is_author"
        }
    ]

    def is_author(self, request, view, action) -> bool:
        article = view.get_object()
        return request.user == article.author
```