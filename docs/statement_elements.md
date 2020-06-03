# Statement Elements

JSON policies are made up of elements that together determine *who* can do *what* with your application and under what *conditions*.

## *principal*

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
            Should match the user of the current request by identifying a group they belong to or their user ID.
        </td>
    </tr>
    <tr>
        <td><b>Special Values</b></td>
        <td>
         <code>"*"</code> (any user) <br> 
         <code>"authenticated"</code> (any authenticated user) <br> 
         <code>"anonymous"</code> (any non-authenticated user)
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td> <code>Union[str, List[str]]</code> </td>
    </tr>
    <tr>
        <td><b>Format</b></td>
        <td>
             Match by group with <code>"group:{name}"</code> <br> 
             Match by ID with <code>"id:{id}" </code>
        </td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
         <code>["group:admins", "id:9322"]</code> <br> 
         <code>["id:5352"]</code> <br> 
         <code>["anonymous"]</code> <br> 
         <code>"*"</code>
        </td>
    </tr>
</table>


## *action*

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
         The action or actions that the statement applies to. The value should match the name of a view set method or the name of the view function.
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td><code>Union[str, List[str]]</code></td>
    </tr>
    <tr>
        <td><b>Special Values</b></td>
        <td>
            <code>"*"</code> (any action) <br> 
            <code>"&lt;safe_methods&gt;"</code> (a read-only HTTP request: HEAD, GET, OPTIONS)
        </td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
            <code>["list", "destroy", "create]</code> <br> 
            <code>["*"]</code> <br> 
            <code>["&lt;safe_methods&gt;"]</code>
        </td>
    </tr>
</table>


## *effect*

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
        Whether the statement, if it is in effect, should allow or deny access. All access is denied by default, so use <code>deny</code> when you'd like to override an <code>allow</code> statement that will also be in effect.
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td><code>str</code></td>
    </tr>
    <tr>
        <td><b>Values</b></td>
        <td>Either <code>"allow"</code> or <code>"deny"</code></td>
    </tr>
</table>


## *condition*

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
        The name of a method on the policy that returns a boolean. The method signature is <code>condition(request, view, action: str, custom_arg: str=None)</code>. If you want to pass a custom argument to the condition's method, format the value as <code>{method_name}:{value}</code>, e.g. <code>user_must_be:owner</code> will call a method named <code>user_must_be</code>, passing it the string <code>"owner"</code> as the final argument. If true, the policy will be in effect. Useful for enforcing object-level permissions. If list of conditions is given, all conditions must evaluate to <code>True</code>.
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td><code>Union[str, List[str]]</code></td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
            <code>"is_manager_of_account"</code> <br>
            <code>"is_author_of_post"</code> <br>
            <code>["balance_is_positive", "account_is_not_frozen"]`</code>
            <br> 
            <code>"user_must_be:account_manager"</code>
        </td>
    </tr>
</table>