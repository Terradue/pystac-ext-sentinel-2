# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for pystac.extensions.sentinel2."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pystac.summaries import RangeSummary
from pystac.utils import str_to_datetime
from pystac.validation import JsonSchemaSTACValidator

import pystac
from pystac import Collection, ExtensionTypeError, Item
from pystac.extensions import sentinel2
from pystac.extensions.sentinel2 import (
    SCHEMA_URI,
    Sentinel2Extension,
    SummariesSentinel2Extension,
)

REFLECTANCE_FACTOR = 1.032
VEGETATION_PERCENTAGE = 34.7
WATER_PERCENTAGE = 1.5
SNOW_PERCENTAGE = 0.2


@pytest.fixture
def validator() -> JsonSchemaSTACValidator:
    validator = JsonSchemaSTACValidator()
    schema_path = Path(__file__).parent / "data" / "sentinel-2-v1.0.0.schema.json"
    validator.schema_cache[SCHEMA_URI] = json.loads(schema_path.read_text())
    return validator


@pytest.fixture
def item() -> Item:
    item = pystac.Item(
        id="sentinel2-item",
        geometry=None,
        bbox=None,
        datetime=datetime(2020, 1, 1, tzinfo=timezone.utc),
        properties={},
    )
    Sentinel2Extension.add_to(item)
    return item


@pytest.fixture
def collection() -> Collection:
    return Collection(
        id="sentinel2-collection",
        description="Synthetic Sentinel-2 collection",
        extent=pystac.Extent(
            pystac.SpatialExtent([-180, -90, 180, 90]),
            pystac.TemporalExtent([[datetime(2020, 1, 1, tzinfo=timezone.utc), None]]),
        ),
        license="proprietary",
    )


def test_stac_extensions(item: Item) -> None:
    assert Sentinel2Extension.has_extension(item)


def test_item_repr(item: Item) -> None:
    assert Sentinel2Extension.ext(item).__repr__() == f"<ItemSentinel2Extension Item id={item.id}>"


def test_no_args_fails_schema_validation(item: Item, validator: JsonSchemaSTACValidator) -> None:
    Sentinel2Extension.ext(item).apply()
    with pytest.raises(pystac.STACValidationError):
        item.validate(validator=validator)


def test_apply_and_validate(item: Item, validator: JsonSchemaSTACValidator) -> None:
    generation_time = str_to_datetime("2020-01-02T03:04:05Z")

    Sentinel2Extension.ext(item).apply(
        tile_id="S2B_OPER_MSI_L2A_TL_SGS__20200102T030405_A012345_T32TQM_N02.09",
        datatake_id="GS2B_20200102T030405_012345_N02.09",
        product_uri="S2B_MSIL2A_20200101T103029_N0213_R108_T32TQM_20200101T132423.SAFE",
        datastrip_id="S2B_OPER_MSI_L2A_DS_SGS__20200102T030405_S20200101T103029_N02.09",
        datatake_type="INS-NOBS",
        generation_time=generation_time,
        processing_baseline="02.13",
        water_percentage=WATER_PERCENTAGE,
        snow_ice_percentage=SNOW_PERCENTAGE,
        vegetation_percentage=VEGETATION_PERCENTAGE,
        reflectance_conversion_factor=REFLECTANCE_FACTOR,
        mgrs_tile="32TQM",
    )

    ext = Sentinel2Extension.ext(item)
    assert ext.tile_id == ("S2B_OPER_MSI_L2A_TL_SGS__20200102T030405_A012345_T32TQM_N02.09")
    assert ext.datatake_id == "GS2B_20200102T030405_012345_N02.09"
    assert ext.product_uri == "S2B_MSIL2A_20200101T103029_N0213_R108_T32TQM_20200101T132423.SAFE"
    assert ext.datastrip_id == "S2B_OPER_MSI_L2A_DS_SGS__20200102T030405_S20200101T103029_N02.09"
    assert ext.datatake_type == "INS-NOBS"
    assert ext.generation_time == generation_time
    assert ext.processing_baseline == "02.13"
    assert ext.water_percentage == WATER_PERCENTAGE
    assert ext.snow_ice_percentage == SNOW_PERCENTAGE
    assert ext.vegetation_percentage == VEGETATION_PERCENTAGE
    assert ext.reflectance_conversion_factor == REFLECTANCE_FACTOR
    assert ext.mgrs_tile == "32TQM"

    item.validate(validator=validator)


def test_processing_baseline_validation(item: Item) -> None:
    with pytest.raises(ValueError, match=r"must match NN.NN"):
        Sentinel2Extension.ext(item).processing_baseline = "2.13"


def test_percentage_validation(item: Item) -> None:
    with pytest.raises(ValueError, match=r"water_percentage"):
        Sentinel2Extension.ext(item).water_percentage = 101


def test_from_dict() -> None:
    document = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "sentinel2-item",
        "properties": {
            "datetime": "2020-01-01T00:00:00Z",
            "s2:tile_id": ("S2A_OPER_MSI_L1C_TL_SGS__20200101T000000_A012345_T32TQM_N02.09"),
            "s2:reflectance_conversion_factor": REFLECTANCE_FACTOR,
        },
        "geometry": None,
        "links": [],
        "assets": {},
        "stac_extensions": [SCHEMA_URI],
    }
    item = pystac.Item.from_dict(document)

    ext = Sentinel2Extension.ext(item)
    assert ext.tile_id == "S2A_OPER_MSI_L1C_TL_SGS__20200101T000000_A012345_T32TQM_N02.09"
    assert ext.reflectance_conversion_factor == REFLECTANCE_FACTOR


def test_to_from_dict(item: Item) -> None:
    generation_time = str_to_datetime("2020-01-02T03:04:05Z")
    Sentinel2Extension.ext(item).apply(
        tile_id="S2A_OPER_MSI_L1C_TL_SGS__20200101T000000_A012345_T32TQM_N02.09",
        generation_time=generation_time,
        water_percentage=WATER_PERCENTAGE,
    )

    document = item.to_dict()
    assert document["properties"][sentinel2.TILE_ID_PROP].startswith("S2A_OPER_MSI_L1C_TL")
    assert document["properties"][sentinel2.GENERATION_TIME_PROP] == "2020-01-02T03:04:05Z"
    assert document["properties"][sentinel2.WATER_PERCENTAGE_PROP] == WATER_PERCENTAGE

    item = pystac.Item.from_dict(document)
    ext = Sentinel2Extension.ext(item)
    assert ext.generation_time == generation_time
    assert ext.water_percentage == WATER_PERCENTAGE


def test_extension_not_implemented(item: Item) -> None:
    item.stac_extensions.remove(Sentinel2Extension.get_schema_uri())

    with pytest.raises(pystac.ExtensionNotImplemented):
        _ = Sentinel2Extension.ext(item)


def test_item_ext_add_to(item: Item) -> None:
    item.stac_extensions.remove(Sentinel2Extension.get_schema_uri())
    assert Sentinel2Extension.get_schema_uri() not in item.stac_extensions

    _ = Sentinel2Extension.ext(item, add_if_missing=True)

    assert Sentinel2Extension.get_schema_uri() in item.stac_extensions


def test_should_raise_exception_when_passing_invalid_extension_object() -> None:
    with pytest.raises(
        ExtensionTypeError,
        match=r"^Sentinel2Extension does not apply to type 'object'$",
    ):
        # Deliberately exercise the runtime guard with an invalid argument.
        Sentinel2Extension.ext(object())  # type: ignore[type-var]


def test_summaries(collection: Collection) -> None:
    summaries_ext = Sentinel2Extension.summaries(collection, True)
    generation_time = RangeSummary(
        str_to_datetime("2020-01-01T00:00:00Z"),
        str_to_datetime("2020-01-02T00:00:00Z"),
    )
    water_percentage = RangeSummary(0.0, 10.0)

    summaries_ext.tile_id = ["32TQM", "32TQL"]
    summaries_ext.generation_time = generation_time
    summaries_ext.water_percentage = water_percentage

    assert summaries_ext.tile_id == ["32TQM", "32TQL"]
    assert summaries_ext.generation_time == generation_time
    assert summaries_ext.water_percentage == water_percentage

    summaries_dict = collection.to_dict()["summaries"]
    assert summaries_dict["s2:tile_id"] == ["32TQM", "32TQL"]
    assert summaries_dict["s2:generation_time"] == {
        "minimum": "2020-01-01T00:00:00Z",
        "maximum": "2020-01-02T00:00:00Z",
    }
    assert summaries_dict["s2:water_percentage"] == {
        "minimum": 0.0,
        "maximum": 10.0,
    }


def test_collection_hint(collection: Collection) -> None:
    with pytest.raises(
        ExtensionTypeError,
        match=r"Hint: Did you mean to use `Sentinel2Extension.summaries` instead\\?",
    ):
        # Collections must use the summaries API.
        Sentinel2Extension.ext(collection)  # type: ignore[type-var]


def test_summaries_ext_add_to(collection: Collection) -> None:
    if Sentinel2Extension.get_schema_uri() in collection.stac_extensions:
        collection.stac_extensions.remove(Sentinel2Extension.get_schema_uri())

    summaries_ext = Sentinel2Extension.summaries(collection, add_if_missing=True)

    assert isinstance(summaries_ext, SummariesSentinel2Extension)
    assert Sentinel2Extension.get_schema_uri() in collection.stac_extensions


@pytest.mark.parametrize("field", sorted(sentinel2.PERCENTAGE_PROPS))
@pytest.mark.parametrize("value", [-1.0, 100.1, float("nan"), float("inf")])
def test_rejects_invalid_percentages(item: Item, field: str, value: float) -> None:
    extension = Sentinel2Extension.ext(item)
    with pytest.raises(ValueError, match=field):
        setattr(extension, field.removeprefix("s2:"), value)
    assert field not in item.properties


@pytest.mark.parametrize("field", ["mean_solar_zenith", "mean_solar_azimuth"])
@pytest.mark.parametrize("value", [-1.0, 180.1, float("nan")])
def test_rejects_invalid_solar_angles(item: Item, field: str, value: float) -> None:
    with pytest.raises(ValueError, match=field):
        setattr(Sentinel2Extension.ext(item), field, value)


@pytest.mark.parametrize("field", ["mean_solar_zenith", "mean_solar_azimuth"])
@pytest.mark.parametrize("value", [0.0, 180.0])
def test_solar_angle_boundaries(
    item: Item, validator: JsonSchemaSTACValidator, field: str, value: float
) -> None:
    extension = Sentinel2Extension.ext(item)
    extension.tile_id = "example-tile"
    setattr(extension, field, value)
    assert getattr(extension, field) == value
    item.validate(validator=validator)


@pytest.mark.parametrize("value", [0.0, 100.0])
@pytest.mark.parametrize("field", sorted(sentinel2.PERCENTAGE_PROPS))
def test_percentage_boundaries(
    item: Item, validator: JsonSchemaSTACValidator, field: str, value: float
) -> None:
    extension = Sentinel2Extension.ext(item)
    extension.tile_id = "example-tile"
    setattr(extension, field.removeprefix("s2:"), value)
    assert item.properties[field] == value
    item.validate(validator=validator)


def test_removing_fields_and_apply_omissions(item: Item) -> None:
    extension = Sentinel2Extension.ext(item)
    extension.apply(tile_id="tile", datatake_id="datatake", water_percentage=WATER_PERCENTAGE)
    extension.water_percentage = None
    assert sentinel2.WATER_PERCENTAGE_PROP not in item.properties
    assert extension.water_percentage is None
    extension.apply(datatake_id="replacement")
    assert sentinel2.TILE_ID_PROP not in item.properties
    assert extension.datatake_id == "replacement"


@pytest.mark.parametrize("value", ["2.13", "0213", "invalid"])
def test_invalid_baselines(item: Item, value: str) -> None:
    with pytest.raises(ValueError, match="processing_baseline"):
        Sentinel2Extension.ext(item).processing_baseline = value


@pytest.mark.parametrize("value", ["32IQM", "32TQZ", "invalid"])
def test_invalid_mgrs_tiles(item: Item, value: str) -> None:
    with pytest.raises(ValueError, match="mgrs_tile"):
        Sentinel2Extension.ext(item).mgrs_tile = value


@pytest.mark.parametrize("field", ["s2:granule_id", "s2:product_type", "s2:water_percentage"])
def test_deprecated_fields_alone_fail_validation(
    item: Item, validator: JsonSchemaSTACValidator, field: str
) -> None:
    item.properties[field] = 1 if field.endswith("percentage") else "example"
    with pytest.raises(pystac.STACValidationError):
        item.validate(validator=validator)


@pytest.mark.parametrize(
    "field",
    [
        "tile_id",
        "datatake_id",
        "product_uri",
        "datastrip_id",
        "datatake_type",
        "reflectance_conversion_factor",
    ],
)
def test_each_current_field_satisfies_schema(
    item: Item, validator: JsonSchemaSTACValidator, field: str
) -> None:
    item.properties[f"s2:{field}"] = 1 if field == "reflectance_conversion_factor" else "example"
    item.validate(validator=validator)


def test_unknown_sentinel2_field_fails_validation(
    item: Item, validator: JsonSchemaSTACValidator
) -> None:
    Sentinel2Extension.ext(item).tile_id = "tile"
    item.properties["s2:unknown"] = "invalid"
    with pytest.raises(pystac.STACValidationError):
        item.validate(validator=validator)


def test_collection_validation_and_summary_removal(
    collection: Collection, validator: JsonSchemaSTACValidator
) -> None:
    summaries = Sentinel2Extension.summaries(collection, add_if_missing=True)
    summaries.tile_id = ["tile"]
    summaries.water_percentage = RangeSummary(0.0, 100.0)
    collection.validate(validator=validator)
    summaries.water_percentage = None
    assert summaries.water_percentage is None
    assert "s2:water_percentage" not in collection.summaries.to_dict()
    summaries.tile_id = None
    with pytest.raises(pystac.STACValidationError):
        collection.validate(validator=validator)
