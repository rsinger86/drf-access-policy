# Policy for Function-Based View

You can also you policies with function-based views. The action to reference in your policy statements is the name of the function. You can also bundle multiple functions into the same policy as the example below shows.

```python
class AuditLogsAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["search_logs"],
            "principal": "group:it_staff",
            "effect": "allow"
        },
        {
            "action": ["download_logs"],
            "principal": ["group:it_admin"],
            "effect": "allow"            
        }
    ]


@api_view(["GET"])
@permission_classes((AuditLogsAccessPolicy,))
def search_logs(request):
    ## you logic here...
    pass


@api_view(["GET"])
@permission_classes((AuditLogsAccessPolicy,))
def download_logs(request):
    ## you logic here...
    pass
```