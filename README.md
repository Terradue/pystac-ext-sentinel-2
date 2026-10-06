<!--
Copyright 2026 Terradue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Sentinel-2 PySTAC extension

[![PyPI - Version](https://img.shields.io/pypi/v/pystac-ext-sentinel-2.svg)](https://pypi.org/project/pystac-ext-sentinel-2)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pystac-ext-sentinel-2.svg)](https://pypi.org/project/pystac-ext-sentinel-2)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/terradue/pystac-ext-sentinel-2/package.yaml?branch=develop&event=push&label=build&logo=githubactions)](https://github.com/terradue/pystac-ext-sentinel-2/actions/workflows/package.yaml?query=branch%3Adevelop)
[![Code coverage](https://img.shields.io/codecov/c/github/terradue/pystac-ext-sentinel-2/develop?logo=codecov)](https://app.codecov.io/gh/terradue/pystac-ext-sentinel-2/tree/develop)

PySTAC implementation of the [Sentinel-2 v1.0.0 STAC Extension](https://github.com/stac-extensions/sentinel-2), with typed Item properties and Collection summaries under the `s2:` prefix. Import `Sentinel2Extension` from `pystac.extensions.sentinel2`.

## Project conventions

This project is templated a Hatch-based Python package with:

- Apache-2.0 license
- Keep a Changelog-compatible `CHANGELOG.md`
- Diátaxis documentation under `docs/`
- top-level `mkdocs.yaml`
- Taskfile integration with `Terradue/taskfile-utils`
- GitHub Actions CI

## Documentation

Read the [project documentation](https://terradue.github.io/pystac-ext-sentinel-2/) for Python examples, the field reference, and API documentation.

To preview it locally:

```bash
hatch run docs:serve
```

Run `hatch run docs:build` to build the documentation with warnings treated as errors.

## Contribute

Submit a [Github issue](/issues) if you have comments or suggestions.

### Local quality checks

Install [Hatch](https://hatch.pypa.io/) and [Taskfiles](https://taskfile.dev/docs/guide) then install the Git hook:

```console
task quality:pre-commit:install
```

Every commit runs Ruff (including the configured McCabe complexity limit),
Ruff formatting, strict mypy checks, and the pytest suite.

Run the complete hook explicitly with:

```console
task quality:pre-commit:run
```

## License

[![Apache License, Version 2.0](https://img.shields.io/badge/license-Apache%20License%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
