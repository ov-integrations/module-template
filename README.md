# module-template

Template repository to create new modules

For Python code follow [style guidelines](https://peps.python.org/pep-0008/)

For configuration installation samples, review files in the `installation` directory

Make sure to rename `.integration_` file to `.integration` for module to be available in the list in UI


## Mirror repository configuration
The provided GitHub Workflow `mirror-repository.yml` automates the synchronization of repositories in different GitHub orgs without using forking.
Steps to setup sync:
1. manually create a mirror of the repository in another organization (assuming the source org is `ov-integrations` and the target is `VizionHub`):
```shell
git clone --mirror https://github.com/ov-integrations/<repo_name>.git
cd <repo_name>
git push --mirror https://github.com/VizionHub/<repo_name>
```

2. generate two PATs to be used for workflow: 
