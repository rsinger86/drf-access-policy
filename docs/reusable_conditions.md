# Re-Usable Conditions/Permissions

If you'd like to re-use custom conditions across policies, you can define them globally in a module and point to it via the setttings. You can also provide a `List` of paths to check multiple files.

```python
# in your project settings.py

DRF_ACCESS_POLICY = {"reusable_conditions": ["myproject.global_access_conditions"]}
```

```python
# in myproject.global_access_conditions.py

def is_the_weather_nice(request, view, action: str) -> bool:
    data = weather_api.load_today()
    return data["temperature"] > 68

def user_must_be(self, request, view, action, field: str) -> bool:
    account = view.get_object()
    return getattr(account, field) == request.user
```

The policy class will first check its own methods for what's been defined in the `condition` property. If nothing is found, it will check the module defined in the `reusable_conditions` setting.
