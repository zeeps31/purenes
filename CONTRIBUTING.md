# Versioning 

This package uses [semantic versioning](https://semver.org/).
Version numbers should adhere to the following:


Given a version number MAJOR.MINOR.PATCH, increment the:

1. MAJOR version when you make incompatible API changes,
2. MINOR version when you add functionality in a backwards compatible manner, and
3. PATCH version when you make backwards compatible bug fixes.
Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.
   
The version can be checked by performing the following:

#### To check the version
```
pysemver check 0.1.0
```

#### To determine the next version 

```
pysemver bump [major | minor | patch] 0.1.0
```

Once the correct version is determined, it should be updated in `setup.py`