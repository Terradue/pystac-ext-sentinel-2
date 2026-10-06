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

# Scope, architecture, and validation

## Package structure

The distribution is named `pystac-ext-sentinel-2`, while the import path is `pystac.extensions.sentinel2`. The wheel excludes the shared `pystac.extensions` initializer owned by PySTAC.

`Sentinel2Extension.ext()` wraps an Item and writes directly into its properties. PySTAC's `to_dict()` handles serialization. The package stores optical mission metadata; it does not process imagery. Assets and item asset definitions are unsupported, matching the upstream extension scope.

These classes are PySTAC property adapters. No generated schema models are maintained. The Taskfile currently imports quality tasks and has no model-generation task.

## Collection summaries

Collections use `Sentinel2Extension.summaries()`. All 26 Item field names are available, with lists for strings, numeric ranges for numbers, and a datetime range for `generation_time`. Summaries are read and replaced without computing them from Items.

## Validation boundaries

Item setters check percentage bounds (0–100 inclusive), the processing baseline pattern (`NN.NN`), the upstream MGRS tile pattern, and legacy solar-angle bounds (0–180 inclusive for both fields). The azimuth limit follows the published schema even though azimuth is often represented using a wider range. Datetime access uses PySTAC's conversion utilities; use timezone-aware values.

These checks are not full schema validation. Annotations do not enforce all runtime types, and reading existing metadata does not rerun setter checks. Summary setters do not validate Item constraints or order range endpoints.

`apply()` mutates fields sequentially and removes omitted fields. If a later setter fails, earlier assignments remain. Validate inputs first if an application requires an all-or-nothing update.

For full STAC and extension validation, install `python -m pip install "pystac[validation]"` and call `item.validate()` or `collection.validate()`. Remote schemas must be accessible or supplied through a configured validator. Neither `apply()` nor `to_dict()` validates the full schema.

The [v1.0.0 schema](https://stac-extensions.github.io/sentinel-2/v1.0.0/schema.json) requires at least one of six current fields in Item properties or Collection summaries. An empty extension or deprecated fields alone fail validation. Undeclared `s2:` fields are rejected on Items, while other prefixes are allowed. The extension schema checks the presence of Collection summary fields but does not check summary values.

Repository tests use the unmodified upstream schema at `tests/data/sentinel-2-v1.0.0.schema.json` in a per-test validator cache, together with PySTAC's bundled core schemas. Validation tests require no schema downloads. Refresh the fixture from upstream when changing the supported specification.

## Migration hooks

`SENTINEL2_EXTENSION_HOOKS` declares the schema identifier, legacy identifier `sentinel-2`, and Item/Collection object types. The module exposes the hook without automatically registering it with PySTAC. It does not move deprecated fields into other extensions.
