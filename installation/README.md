It is recommended to combine all related OneVizion configuration objects into the single `Components Package`.

All configuration object names should be prefixed with the unique prefix to avoid naming collisions with existing configuration or installed modules during the deployment.
Start prefix with `VHM` (VizionHub Module), i.e. `VHMBI` for the `BI Tables` module, `VHMREQ` for the `Requirements` module.

For example, names of Trackor Types related to the BI Tables module: `VHMBI_FIELD`, `VHMBI_TABLE`, though component labels do not need to include any prefixes, as well as Config Field names as they are unique by Trackor Type.

Use `<PREFIX>_PKG` format for the PL/SQL package names, and add an additional suffix when there is more than one package in the module.
