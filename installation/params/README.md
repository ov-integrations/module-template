## Module Params
Module-level param provides functionality to set user-defined, custom parameters in the Module Wizard.
Supported types are:
| ID  | Type |
| ------------- | ------------- |
| 0  | Text  |
| 1  | Number  |
| 3  | Yes/No  |
| 8  | Password  |
| 90  | SQL Query Selector  |
| 150  | User Selector  |
| 160  | Latitude  |
| 170  | Longitude  |

They can be accessible while installation/upgrade/uninstallation or after them through `util_module` functions or with `{ParamName}` so they can be generated dynamically inside of (md,xml,sql,csv) files.

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
