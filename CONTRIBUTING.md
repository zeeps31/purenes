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

# Commit Messages 

This package uses the [python-semantic-release](https://github.com/relekang/python-semantic-release)
package to handle versioning and releases. Commit messages need to adhere to 
the [angular commit guidelines](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits)
to be compatible with the python-semantic-release package. 

To verify that the commit message adheres to the correct guidelines, the 
following command can be executed. 

Example commit message:

```
feat: add semantic versioning
```

Testing the version change:

```
semantic-release print-version
```

Example output:

```
0.24.0
```

If you are still unsure how to describe the change correctly feel free to ask 
in your PR. 

# Releases

This package is released by the [python-semantic-release](https://github.com/relekang/python-semantic-release)
package on each push to main. If there are changes that result in a new release
it will happen when the build is green, and the change is merged into main. 