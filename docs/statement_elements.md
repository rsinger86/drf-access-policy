# Statement Elements

JSON policies are made up of elements that together determine _who_ can do _what_ with your application and under what _conditions_.

## _principal_

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
            <ul>
                <li>
                    <code>"*"</code> (any user)
                </li>
                <li>
                    <code>"admin"</code> (any admin user)
                </li>
                <li>
                    <code>"staff"</code> (any staff user)
                </li>
                <li>
                    <code>"authenticated"</code> (any authenticated user)
                </li>
                <li>
                    <code>"anonymous"</code> (any non-authenticated user)
                </li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td> <code>Union[str, List[str]]</code> </td>
    </tr>
    <tr>
        <td><b>Formats</b></td>
        <td>
            <ul>
                <li>
                   Match by group with <code>"group:{name}"</code>
                </li>
                <li>
                   Match by ID with <code>"id:{id}" </code>
                </li>
            </ul>      
        </td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
            <ul>
                <li>
                   <code>["group:admins", "id:9322"]</code>
                </li>
                <li>
                   <code>["id:5352"]</code>
                </li>
                <li>
                    <code>["anonymous"]</code> 
                </li>
                <li>
                    <code>"*"</code>
                </li>
            </ul>
        </td>
    </tr>
</table>

## _action_

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
         The action or actions that the statement applies to. The value should match the name of a view set method or the name of the view function. <br><br> Alternatively, you can use placeholders to match the current request's HTTP method.
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td><code>Union[str, List[str]]</code></td>
    </tr>
    <tr>
        <td><b>Special Values</b></td>
        <td>
            <ul>
                <li>
                    <code>"*"</code> (any action)
                </li>
                <li>
                    <code>"&lt;safe_methods&gt;"</code> (a read-only HTTP request: HEAD, GET, OPTIONS)
                </li>
                <li>
                    <code>"&lt;method:get|head|options|delete|put|patch|post&gt;"</code> (match a specific HTTP method)
                </li>
            </ul>
        </td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
            <ul>
                <li>
                    <code>["list", "destroy", "create]</code>
                </li>
                <li>
                    <code>["*"]</code> 
                </li>
                <li>
                    <code>["&lt;safe_methods&gt;"]</code> <br>
                </li>
                <li>
                     <code>["&lt;method:post&gt;"]</code>
                </li>
            </ul>
        </td>
    </tr>
</table>

## _effect_

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
        <td>
            <ul>
                <li>
                   <code>"allow"</code>
                </li>
                <li>
                   <code>"deny"</code>
                </li>
            </ul>
        </td>
    </tr>
</table>

## _condition_

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
        The name of a method on the policy that returns a boolean. If you want to pass a custom argument to the condition's method, format the value as <code>{method_name}:{value}</code>, e.g. <code>user_must_be:owner</code> will call a method named <code>user_must_be</code>, passing it the string <code>"owner"</code> as the final argument.
        <br><br>
         The method signature is <code>condition(request, view, action: str, custom_arg: str=None)</code>. If it returns <code>True</code>, the statement will be in effect.
         <br><br>
         Useful for enforcing object-level permissions. If list of conditions is given, all conditions must evaluate to <code>True</code>.
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td><code>Union[str, List[str]]</code></td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
            <ul>
                <li>
                   <code>"is_manager_of_account"</code> 
                </li>
                <li>
                   <code>"is_author_of_post"</code>
                </li>
                <li>
                    <code>["balance_is_positive", "account_is_not_frozen"]`</code>
                </li>
                <li>
                    <code>"user_must_be:account_manager"</code>
                </li>
            </ul>
        </td>
    </tr>
</table>

## _condition_expression_

<table>
    <tr>
        <td><b>Description</b></td>
        <td>
        Same as the *condition` element, but with added support for evaluating boolean combinations of policy methods. The expressions follow Python's boolean syntax.
        <br><br>
         The method signature is <code>condition(request, view, action: str, custom_arg: str=None)</code>. If it returns <code>True</code>, the statement will be in effect.
        </td>
    </tr>
    <tr>
        <td><b>Type</b></td>
        <td><code>Union[str, List[str]]</code></td>
    </tr>
    <tr>
        <td><b>Examples</b></td>
        <td>
            <ul>
                <li>
                    <code>["(is_request_from_account_owner or is_FBI_request)"]</code>
                </li>
                <li>
                    <code>"is_sunny and is_weekend"</code>
                </li>
                <li>
                    <code>"is_tasty and not is_expensive"</code>
                </li>
            </ul>
        </td>
    </tr>
</table>
