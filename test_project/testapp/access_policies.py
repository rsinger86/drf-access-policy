from rest_access_policy import AccessPolicy


class UserAccountAccessPolicy(AccessPolicy):
    statements = [
        {"principal": "group:admin", "action": "create", "effect": "allow"},
        {"principal": "group:banned", "action": "retrieve", "effect": "deny"},
    ]
