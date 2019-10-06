# Object-Level Permissions/Custom Conditions

What about object-level permissions? You can easily check object-level access in a custom condition that's evaluated to determine whether the statement takes effect. This condition is passed the `view` instance, so you can  get the model instance with a call to `view.get_object()`. You can even reference multiple conditions, to keep your access methods focused and testable, as well as parametrize these conditions with arguments.

```python hl_lines="14 25"
class AccountAccessPolicy(AccessPolicy):
    statements = [
        ## ... other statements ...
        {
            "action": ["withdraw"],
            "principal": ["*"],
            "effect": "allow",
            "condition": ["balance_is_positive", "user_must_be:owner"]     
        },
        {
            "action": ["upgrade_to_gold_status"],
            "principal": ["*"],
            "effect": "allow",
            "condition": ["user_must_be:account_advisor"]
        }
        ## ... other statements ...
    ]

    def balance_is_positive(self, request, view, action) -> bool:
        account = view.get_object()
        return account.balance > 0

    def user_must_be(self, request, view, action, field: str) -> bool:
        account = view.get_object()
        return getattr(account, field) == request.user
```

Notice how we're re-using the `user_must_be` method by parameterizing it with the model field that should be equal fo the user of the request: the statement will only be effective if this condition passes.
