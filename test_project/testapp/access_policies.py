from rest_access_policy import AccessPolicy


def is_account_mario(instance):
    return instance.username == "mario"

class UserAccountAccessPolicy(AccessPolicy):
    statements = [
        {"principal": "group:admin", "action": ["create", "update"], "effect": "allow"},
        {
            "principal": "group:dev",
            "action": ["update", "partial_update"],
            "effect": "allow",
        },
        {"principal": "group:banned", "action": "retrieve", "effect": "deny"},
        {
            "principal": "group:regular_users",
            "action": "set_password",
            "effect": "allow",
        },
    ]

    field_permissions = {"read_only": [{"principal": "group:dev", "fields": "status"},
                                       {"principal": "*", "fields": "last_name","condition":[is_account_mario]}]}



class LogsAccessPolicy(AccessPolicy):
    statements = [
        {"principal": "group:admin", "action": "*", "effect": "allow"},
        {"principal": "group:dev", "action": "get_logs", "effect": "allow"},
        {"principal": "group:dev", "action": "delete_logs", "effect": "deny"},
    ]


class LandingPageAccessPolicy(AccessPolicy):
    statements = [
        {"principal": ["anonymous", "authenticated"], "action": "*", "effect": "allow"},
    ]
