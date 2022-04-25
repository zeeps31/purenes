# Adding Tests

### Naming Guidelines

The test naming conventions defined in PureNES are based on the ideas
defined in this [post](https://stackoverflow.com/questions/155436/unit-test-naming-best-practices).

When naming a test, the name should attempt to adhere to the following 
guidelines: 

* No rigid naming policy
* Name the test as if you were describing the scenario to a non-programmer
* Separate words by underscores

The name of the test should describe what it accomplishes without including 
technical details that may change over time. 

**Note:** The test must still include the "test" prefix to make it discoverable 
by pytest. 

Bad Examples:

`test_clock_scanline_260_resets_scanline_counter`

`test_clock_cycle_340_resets_cycle_counter`

`test_read_invalid_address_throws_exception`


Good Examples (same test names adjusted to adhere to naming guidelines):

`test_scanline_resets_at_maximum`

`test_cycle_resets_at_maximum`

`test_read_from_an_incorrect_address_is_invalid`


More information about this naming policy can be found in this 
[article](https://enterprisecraftsmanship.com/posts/you-naming-tests-wrong/).

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