# Policy for ViewSet

A policy is comprised of "statements" that declare what "actions" a "principal" can or cannot perform on the resource, with optional custom checks that can examine any detail of the current request.

Two key points to remember going forward:

* all access is implicitly denied by default
* any statement with the "deny" effect overrides any and all "allow" statement

Let's look at the policy below, which is for an articles endpoint exposed through a `ViewSet`.

```python hl_lines="9"
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
            "action": ["destroy"],
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
```

The actions correspond to the names of methods on the ViewSet and the following rules are put in place:

- anyone is allowed to list and retrieve articles
- users in the editor group are allowed to publish and unpublish articles
- in order to destroy an article, the user must be the author of the article. Notice how the condition method `is_author` calls `get_object()` on the view to get the current article.
- if the condition `is_happy_hour`, evaluates to `True`, then no one is allowed to do anything.

Additionally, we have some logic in the `scope_queryset` method for filtering which models are visible to the current user. Here, we want users to only see published articles, unless they are an editor, in which case they case see articles with any status. You have to remember to call this method from the view, so I'd suggest reviewing this as part of a security audit checklist.

Below is a `ViewSet` with the policy attached. Notice how the `publish` and `unpublish` methods correspond to the `action` declarations in the policy.

```python hl_lines="20 24"
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