## Module Params
Module-level param provides functionality to set user-defined, custom parameters in the Module Wizard.
Supported types are:
| Property  | Description |
| ------------- | ------------- |
| name  | Parameter name that should be in CamelCase  |
| typeId  | 0, 1, 3, 8, 90, 150, 160, 170 (Text, Number, Yes/No, Password, SQL Query Selector, User Selector, Latitude, Longitude)  |
| value  | Empty or pre-defined value  |
| paramSql  | SQL statement to interact with the user enviroment  |
| description  | Description for the parameter |
| isReadOnly  | Control modifying access after installation/upgrade   |
| isHidden  | If true will not be displayed and skipped  |

They can be accessible while installation/upgrade/uninstallation or after them through `util_module` functions or with `{ParamName}` placeholder so they can be generated dynamically inside of (md,xml,sql,csv) files.

```sql
--- SQL Usage
util.newtrackor(id.{ParamName}.tt)
--or
util_module.get_module_param_val(:p_module_id, 'ParamName')
```

``````xml
<!--XML Usage-->
<TRACKOR_TYPE>{ParamName}</TRACKOR_TYPE> 
``````

```CSV
---CSV Usage
{VendorTrackorType} ID
VHMBOS-{VendorTrackorType}
```
