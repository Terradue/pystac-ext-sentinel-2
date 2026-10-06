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

# Work with Sentinel-2 metadata

The examples continue from the Item and imports created in the [tutorial](../tutorials/first-steps.md).

## Update or remove one field

```python
sentinel2 = Sentinel2Extension.ext(item)
sentinel2.datatake_type = "INS-NOBS"
sentinel2.product_uri = None
assert "s2:product_uri" not in item.properties
```

`ext(item)` requires the extension to be declared already. Use `add_if_missing=True` when first attaching it. Assigning `None` removes a field. `apply()` sets every field and removes omitted values; individual setters preserve other fields.

## Read legacy metadata

```python
sentinel2.generation_time = acquisition_datetime
sentinel2.processing_baseline = "05.09"
sentinel2.water_percentage = 1.5
assert sentinel2.generation_time == acquisition_datetime
assert item.properties["s2:processing_baseline"] == "05.09"
```

These properties support older catalogs. For new products, follow the [upstream replacements](../reference/fields.md#deprecated-fields). No automatic migration or deprecation warnings are provided.

## Manage Collection summaries

```python
from pystac.summaries import RangeSummary

collection = pystac.Collection(
    id="example-sentinel-2-collection",
    description="Synthetic Sentinel-2 products",
    extent=pystac.Extent(
        pystac.SpatialExtent([-180, -90, 180, 90]),
        pystac.TemporalExtent([[acquisition_datetime, None]]),
    ),
    license="proprietary",
)
summaries = Sentinel2Extension.summaries(collection, add_if_missing=True)
summaries.datatake_type = ["INS-NOBS"]
summaries.reflectance_conversion_factor = RangeSummary(1.0, 1.04)
summaries.generation_time = RangeSummary(acquisition_datetime, acquisition_datetime)
assert collection.summaries.to_dict()["s2:datatake_type"] == ["INS-NOBS"]
summaries.generation_time = None
assert "s2:generation_time" not in collection.summaries.to_dict()
```

String summaries use `list[str]`, numeric summaries use `RangeSummary[float]`, and `generation_time` uses `RangeSummary[datetime]`. Setters replace whole summaries; they do not aggregate Items or apply Item setter checks. The summary wrapper has no `apply()` method. At least one of the six current fields must occur in summaries for upstream schema validation.

## Supported objects

`Sentinel2Extension.ext()` accepts Items. Collections use `summaries()`. Assets and item asset definitions have no wrappers.
