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

`pystac-ext-sentinel-2` reads and writes Sentinel-2 metadata in PySTAC Item properties and Collection summaries using the `s2:` prefix. Import `Sentinel2Extension` from `pystac.extensions.sentinel2`.

The implementation targets the [upstream Sentinel-2 v1.0.0 specification](https://github.com/stac-extensions/sentinel-2) and declares `https://stac-extensions.github.io/sentinel-2/v1.0.0/schema.json`. Upstream classifies the extension as Candidate. The package version is independent of the specification version.

```bash
python -m pip install pystac-ext-sentinel-2
```

- [Create a Sentinel-2 Item](tutorials/first-steps.md) and round-trip its metadata.
- [Update fields and Collection summaries](how-to/use-extension.md).
- [Look up fields and deprecated replacements](reference/fields.md).
- [Browse the Python API](reference/api.md).
- [Understand validation and scope](explanation/architecture.md).

Six current mission-specific fields and twenty legacy fields are supported. Deprecated properties remain available for existing catalogs; prefer their upstream replacements for new metadata.
