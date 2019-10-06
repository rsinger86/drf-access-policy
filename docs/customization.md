# Customizing User Group/Role Values

If you aren't using Django's built-in auth app, you may need to define a custom way to retrieve the role/group names to which the user belongs. Just define a method called `get_user_group_values` on your policy class. It is passed a single argument: the  user of the current request. In the example below, the user model has a to-many relationship with a "roles", which have their "name" value in a field called "title".

```python
class UserAccessPolicy(AccessPolicy):
    # ... other properties and methods ...

    def get_user_group_values(self, user) -> List[str]:
        return list(user.roles.values_list("title", flat=True))
```
# Customizing Principal Prefixes

By default, the prefixes to identify the type of principle (user or group) are "id:" and "group:", respectively. You can customize this by setting these properties on your policy class:

```python
class FriendRequestPolicy(permissions.BasePermission):
    group_prefix = "role:"
    id_prefix = "staff_id:"

    # .. the rest of you policy definition ..
```
