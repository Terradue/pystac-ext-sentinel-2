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

# Sentinel-2 fields

The [upstream specification](https://github.com/stac-extensions/sentinel-2) and [v1.0.0 JSON Schema](https://stac-extensions.github.io/sentinel-2/v1.0.0/schema.json) define the contract. Python property names match JSON names with `s2:` removed. All getters can return `None`; setting `None` removes the field.

## Current fields

| STAC field | Python property | Item value |
| --- | --- | --- |
| `s2:tile_id` | `tile_id` | `str`: tile identifier |
| `s2:datatake_id` | `datatake_id` | `str`: datatake identifier |
| `s2:product_uri` | `product_uri` | `str`: product URI |
| `s2:datastrip_id` | `datastrip_id` | `str`: datastrip identifier |
| `s2:datatake_type` | `datatake_type` | `str`: datatake type |
| `s2:reflectance_conversion_factor` | `reflectance_conversion_factor` | `float`: reflectance conversion factor |

At least one of these six fields must exist in Item properties or Collection summaries for schema validation. The schema imposes no string pattern on the current identifiers and no bounds on the conversion factor.

## Deprecated fields

The upstream README deprecates the following fields. They remain readable and writable for compatibility, without automatic migration or warnings. Percentage deprecations in the README are not marked with `deprecated` in the published JSON Schema.

| STAC field / Python property | Item value | Upstream replacement |
| --- | --- | --- |
| `s2:granule_id` / `granule_id` | `str` | `s2:tile_id` |
| `s2:product_type` / `product_type` | `str` | `product:type` |
| `s2:generation_time` / `generation_time` | `datetime` | `processing:datetime` |
| `s2:processing_baseline` / `processing_baseline` | `str`, pattern `NN.NN` | `processing:version` |
| `s2:mgrs_tile` / `mgrs_tile` | `str`, e.g. `32TQM` | MGRS extension fields and `grid:code` |
| `s2:mean_solar_zenith` / `mean_solar_zenith` | `float`, 0–180 degrees | `view:sun_elevation`, calculated as 90 minus zenith |
| `s2:mean_solar_azimuth` / `mean_solar_azimuth` | `float`, 0–180 degrees in the schema | `view:sun_azimuth` |
| `s2:snow_ice_percentage` / `snow_ice_percentage` | `float`, 0–100 | `eo:snow_cover` |
| `s2:water_percentage` / `water_percentage` | `float`, 0–100 | `statistics.water` |
| `s2:vegetation_percentage` / `vegetation_percentage` | `float`, 0–100 | `statistics.vegetation` |
| `s2:thin_cirrus_percentage` / `thin_cirrus_percentage` | `float`, 0–100 | `statistics.thin_cirrus` |
| `s2:cloud_shadow_percentage` / `cloud_shadow_percentage` | `float`, 0–100 | `statistics.cloud_shadow` |
| `s2:nodata_pixel_percentage` / `nodata_pixel_percentage` | `float`, 0–100 | `statistics.nodata_pixel` |
| `s2:unclassified_percentage` / `unclassified_percentage` | `float`, 0–100 | `statistics.unclassified` |
| `s2:dark_features_percentage` / `dark_features_percentage` | `float`, 0–100 | `statistics.dark_features` |
| `s2:not_vegetated_percentage` / `not_vegetated_percentage` | `float`, 0–100 | `statistics.not_vegetated` |
| `s2:degraded_msi_data_percentage` / `degraded_msi_data_percentage` | `float`, 0–100 | `statistics.degraded_msi_data` |
| `s2:high_proba_clouds_percentage` / `high_proba_clouds_percentage` | `float`, 0–100 | `statistics.high_proba_clouds` |
| `s2:medium_proba_clouds_percentage` / `medium_proba_clouds_percentage` | `float`, 0–100 | `statistics.medium_proba_clouds` |
| `s2:saturated_defective_pixel_percentage` / `saturated_defective_pixel_percentage` | `float`, 0–100 | `statistics.saturated_defective_pixel` |

For `statistics`, the table uses dotted notation to identify the suggested entry name, not a literal STAC property name. Follow the [common metadata statistics definition](https://github.com/radiantearth/stac-spec/blob/master/commons/common-metadata.md#statistics) for the entry structure. The upstream convention removes `s2:` and `_percentage` from the original name. Snow/ice has the specific replacement `eo:snow_cover`.

## Access and validation

Datetime values serialize to strings and parse back through PySTAC's datetime utilities. Use timezone-aware datetimes. Item setters reject out-of-range percentages and solar angles, malformed baselines, and MGRS tiles that fail the schema pattern with `ValueError`. These setters do not provide complete schema validation. Existing metadata is not revalidated when read.

`apply()` replaces all 26 fields and clears omitted values. Individual setters affect only their corresponding property. See [validation boundaries](../explanation/architecture.md#validation-boundaries) for full validation and partial-update behavior.

## Collection summaries

`Sentinel2Extension.summaries(collection)` exposes all 26 properties. Strings use `list[str]`, numeric fields use `RangeSummary[float]`, and `generation_time` uses `RangeSummary[datetime]` with serialized string bounds. Getters return `None` when the corresponding summary form is absent. Assigning `None` removes the summary.

Setters replace whole summaries without aggregating Items or checking Item field constraints. The upstream extension schema requires a current summary field but does not validate its summary values.
