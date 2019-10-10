# Integration-Template

The Integration-Template is a template for creating integrations.
 
## Repository Name 
The Repository Name matches to Integration Name.
 
## Content

### .integration
.integration - config file which contains:
- command - that runs the integration
- settings_file_name - that contains additional settings
- default_schedule - that contains default schedule (must be specified in the quartz cron expression format)
- read_from_stdout - checkbox that indicates that STDOUT is added to Log Trackor

Example:
```
command = python3 ./SampleIntegration.py
settings_file_name = settings
default_schedule = 0 0 0/1 * * ?
read_from_stdout = false
```

### settings
settings - a file with settings, the name of which can be anything. Integration uses settings file, for example, to get username, password, URL, type. The content and structure of settings file may vary depending on the integration requirements.

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

### components.xml
Integration may require some configuration changes. Configuration is standard part of integration and stored in components.xml file. Configuration changes will be applied as part of integration installation.

## Version
Versions for integration match to the repository tags. If there are no tags, then the Master branch is used.
 
## Installation
The list of available integrations for installation contains only those repositories that contain .integration config file.

The following fields are populated during installation:
- [Source -> Field]
- Repository Name -> Integration Name
- Repository Description -> Description
- Repository URL -> Repository URL
- .integration -> command, settings_file_name, default_schedule, read_from_stdout
- SettingsFileTemplate.integration -> Settings File
- Selected Tag -> Version
