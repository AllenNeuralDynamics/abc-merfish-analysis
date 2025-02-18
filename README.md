# abc-merfish-analysis

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: conventionalcommits](https://img.shields.io/badge/semantic--release-conventionalcommits-e10079?logo=conventionalcommits)](https://github.com/semantic-release/semantic-release)
![Python](https://img.shields.io/badge/python->=3.8-blue?logo=python)

Shared tools for accessing and processing ABC Atlas MERSCOPE data.

## Usage
 See usage examples in the accompanying notebook repository: https://github.com/AllenNeuralDynamics/thalamus-merfish-analysis

## Installation
To use the software, install from github via
```bash
pip install git+https://github.com/AllenNeuralDynamics/abc-merfish-analysis
```
For the full functionality (unless just using to load data), install with the "plot" extras:
```bash
pip install git+https://github.com/AllenNeuralDynamics/abc-merfish-analysis[plot]
```

## Contributing


### Pull requests

For internal members, please create a branch. For external members, please fork the repository and open a pull request from the fork. We'll primarily use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) style for commit messages. Roughly, they should follow the pattern:
```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

where type is one of:

- **fix**: A bugfix
- **feat**: A new feature
- **build**: Changes that affect build tools or external dependencies (example scopes: pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts (examples: .github/workflows/ci.yml)
- **docs**: Documentation only changes
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests

### Semantic Release

The table below, from [semantic release](https://github.com/semantic-release/semantic-release), shows which commit message gets you which release type when `semantic-release` runs (using the default configuration):

| Commit message                                                                                                                                                                                   | Release type                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `fix(pencil): stop graphite breaking when too much pressure applied`                                                                                                                             | ~~Patch~~ Fix Release, Default release                                                                          |
| `feat(pencil): add 'graphiteWidth' option`                                                                                                                                                       | ~~Minor~~ Feature Release                                                                                       |
| `perf(pencil): remove graphiteWidth option`<br><br>`BREAKING CHANGE: The graphiteWidth option has been removed.`<br>`The default graphite width of 10mm is always used for performance reasons.` | ~~Major~~ Breaking Release <br /> (Note that the `BREAKING CHANGE: ` token must be in the footer of the commit) |

