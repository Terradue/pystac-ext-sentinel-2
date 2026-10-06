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

# Create a Sentinel-2 Item

[Install the package](../how-to/install.md), then run this complete example with synthetic metadata:

```python
from datetime import datetime, timezone

import pystac
from pystac.extensions.sentinel2 import Sentinel2Extension

acquisition_datetime = datetime(2023, 2, 1, tzinfo=timezone.utc)
item = pystac.Item(
    id="example-sentinel-2",
    geometry=None,
    bbox=None,
    datetime=acquisition_datetime,
    properties={},
)
sentinel2 = Sentinel2Extension.ext(item, add_if_missing=True)
sentinel2.apply(
    tile_id="S2B_OPER_MSI_L2A_TL_SGS__20230201T120000_A030000_T32TQM_N05.09",
    datatake_id="GS2B_20230201T103029_030000_N05.09",
    datatake_type="INS-NOBS",
    reflectance_conversion_factor=1.032,
)
serialized = item.to_dict()
assert Sentinel2Extension.get_schema_uri() in serialized["stac_extensions"]
assert serialized["properties"]["s2:datatake_type"] == "INS-NOBS"
restored = Sentinel2Extension.ext(pystac.Item.from_dict(serialized))
assert restored.tile_id == sentinel2.tile_id
assert restored.reflectance_conversion_factor == sentinel2.reflectance_conversion_factor
```

At least one of `tile_id`, `datatake_id`, `product_uri`, `datastrip_id`, `datatake_type`, or `reflectance_conversion_factor` is required for schema validation. Calling `apply()` without arguments clears all supported fields, so the resulting empty extension fails validation.

`to_dict()` serializes without running JSON Schema validation. With the `pystac[validation]` extra installed and schemas accessible, validate the complete Item:

```python
item.validate()
```

See [validation boundaries](../explanation/architecture.md#validation-boundaries) for details.
