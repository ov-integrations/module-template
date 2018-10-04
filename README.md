# Integration-Template

The Integration-Template is a template for creating integrations.
 
## Repository Name 
The Repository Name matches to Integration Name.
 
## Content

### .integration
.integration - Config file which contains the command that runs the integration.

Example:
```
command = python3 ./SampleIntegration.py
```

### SettingsFileTemplate.integration
SettingsFileTemplate.integration is a template for Settings File. Integration uses SettingsFile, for example, to get username, password, URL, type. The content and structure of SettingsFileTemplate.integration may vary depending on the integration requirements.

Example:
```
SET=daily
UN=username
PWD=password
URL=https://name.onevizion.com
```
### Icon
icon.png is an icon for integration.

The icon must be:
- In PNG (.png) file format
- 60x60px

Example:  
 ![example](./icon.png)

## Version
Versions for integration match to the repository tags. If there are no tags, then the Master branch is used.
 
## Installation
The list of available integrations for installation contains only those repositories that contain .integration config file.

The following fields are populated during installation:
- [Source -> Field]
- Repository Name -> Integration Name
- Repository Description -> Description
- Repository URL -> Repository URL
- .integration -> Command
- SettingsFileTemplate.integration -> Settings File
- Selected Tag -> Version
