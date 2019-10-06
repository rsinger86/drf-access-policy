# Loading Statements from External Source

If you don't want your policy statements hardcoded into the classes, you can load them from an external data source: a great step to take because you can then change access rules without redeploying code. 

Just define a method on your policy class called `get_policy_statements`, which has the following signature:
`get_policy_statements(self, request, view) -> List[dict]`

Example:

```python
class UserAccessPolicy(AccessPolicy):
    id = 'user-policy'

    def get_policy_statements(self, request, view) -> List[dict]:
        statements = data_api.load_json(self.id)
        return json.loads(statements)
```

You probably want to only define this method once on your own custom subclass of `AccessPolicy`, from which all your other access policies inherit.