# Multitenancy Data / Restricting QuerySets

You can define a class method on your policy class that takes a `QuerySet` and the current request and returns a securely scoped `QuerySet` representing only the database rows the current user should have access to. This is helpful for multitenant situations or more generally when users should not have full visibility to model instances. You could do this elsewhere in your code, but putting this method on the policy class keeps all access logic in a single place.

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

You have to remember to call `scope_queryset` method from the view, so I'd suggest reviewing this as part of a security audit checklist.

```python
    class PhotoAlbumViewSet(ModelViewSet):
    # ...

        # Ensure that current user only access albums created by himself
        def get_queryset(self):
            return self.access_policy.scope_queryset(
                self.request, PhotoAlbum.objects.all()
            )
```

Note that the if [ViewSet Mixin](view_set_mixin.md) is used, the `get_queryset` method is overrided automatically based in the current view's queryset.
