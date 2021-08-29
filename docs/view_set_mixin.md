# ViewSet Mixin

Most likely, you'll only have one access policy per `ViewSet`, to keep all the logic in one place for each resource. Django REST Framework allows setting multiple permission classes, which can make `ViewSet` code less clear. For clarity, a mixin is provided that allows you define to an `access_policy` class attribute. The mixin will add the policy class to the view's `permission_classes` to ensure DRF's request handler evaluates it.

```python
from my_app_policies import ArticleAccessPolicy
from rest_access_policy import AccessViewSetMixin


class ArticleViewSet(AccessViewSetMixin, ModelViewSet):
    access_policy = ArticleAccessPolicy

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, Articles.objects.all()
        )
```
