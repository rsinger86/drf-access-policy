# Migrating to 1.0

The 1.0 version introduced a breaking change for projects that use the `condition` element to combine multiple condition methods with boolean logic.

Projects that use the `condition` element in this way must update affected statements to use the `condition_expression` element instead, which evaluates expressions in the same way that occurred prior to 1.0.

:no_entry_sign: **No longer works**

```python
class EmailAccountAccessPolicy(AccessPolicy):
    statements = [
        {
            "principal": "authenticated",
            "action": "read",
            "effect": "allow",
            "condition": "is_owner or is_NSA"
        },
    ]
```

:green_circle: **Change to**

```python
class EmailAccountAccessPolicy(AccessPolicy):
    statements = [
        {
            "principal": "authenticated",
            "action": "read",
            "effect": "allow",
            "condition_expression": "is_owner or is_NSA"
        },
    ]
```
