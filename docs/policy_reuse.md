# Access Policy Re-Use

If you've defined a `scope_queryset` method, you'll likely want to use it in multiple places. If an object shouldn't be returned to a user from a view set, they probably shouldn't be able to reference that object when sending a `POST` or `PUT` request.

A `PermittedPkRelatedField`, `PermittedSlugRelatedField` or `PermittedHyperlinkedRelatedField` can be passed an access policy class.

```python
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_access_policy import PermittedPkRelatedField
from my_policies import UserAccessPolicy

class AccountUpdateSerializer(serializers.ModelSerializesr):
    emergency_contact = PermittedPkRelatedField(
        access_policy=UserAccessPolicy, queryset=User.objects.all()
    )
```

```python
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_access_policy import PermittedSlugRelatedField
from my_policies import UserAccessPolicy

class AccountUpdateSerializer(serializers.ModelSerializesr):
    emergency_contact = PermittedSlugRelatedField(
        access_policy=UserAccessPolicy, queryset=User.objects.all(), slug_field="username"
    )
```

```python
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_access_policy import PermittedHyperlinkedRelatedField
from my_policies import UserAccessPolicy

class AccountUpdateSerializer(serializers.HyperlinkedModelSerializer):
    emergency_contact = PermittedHyperlinkedRelatedField(
        access_policy=UserAccessPolicy, queryset=User.objects.all(), view_name="user-detail"
    )
```

Ensure that when the serializer is instantiated, it gets passed the `request` object, which
gets passed to the policy's `scope_queryset` behind the scenes.
