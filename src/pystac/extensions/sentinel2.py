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

"""Read and write Sentinel-2 v1.0.0 Item properties and Collection summaries."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, ClassVar, Generic, Literal, TypeVar, cast

from pystac.extensions.base import (
    ExtensionManagementMixin,
    PropertiesExtension,
    SummariesExtension,
)
from pystac.extensions.hooks import ExtensionHooks
from pystac.summaries import RangeSummary
from pystac.utils import datetime_to_str, map_opt, str_to_datetime

import pystac

if TYPE_CHECKING:
    from datetime import datetime

T = TypeVar("T", bound=pystac.Item)

SCHEMA_URI = "https://stac-extensions.github.io/sentinel-2/v1.0.0/schema.json"
PREFIX = "s2:"

TILE_ID_PROP = PREFIX + "tile_id"
GRANULE_ID_PROP = PREFIX + "granule_id"
DATATAKE_ID_PROP = PREFIX + "datatake_id"
PRODUCT_URI_PROP = PREFIX + "product_uri"
DATASTRIP_ID_PROP = PREFIX + "datastrip_id"
PRODUCT_TYPE_PROP = PREFIX + "product_type"
DATATAKE_TYPE_PROP = PREFIX + "datatake_type"
GENERATION_TIME_PROP = PREFIX + "generation_time"
PROCESSING_BASELINE_PROP = PREFIX + "processing_baseline"
WATER_PERCENTAGE_PROP = PREFIX + "water_percentage"
MEAN_SOLAR_ZENITH_PROP = PREFIX + "mean_solar_zenith"
MEAN_SOLAR_AZIMUTH_PROP = PREFIX + "mean_solar_azimuth"
SNOW_ICE_PERCENTAGE_PROP = PREFIX + "snow_ice_percentage"
VEGETATION_PERCENTAGE_PROP = PREFIX + "vegetation_percentage"
THIN_CIRRUS_PERCENTAGE_PROP = PREFIX + "thin_cirrus_percentage"
CLOUD_SHADOW_PERCENTAGE_PROP = PREFIX + "cloud_shadow_percentage"
NODATA_PIXEL_PERCENTAGE_PROP = PREFIX + "nodata_pixel_percentage"
UNCLASSIFIED_PERCENTAGE_PROP = PREFIX + "unclassified_percentage"
DARK_FEATURES_PERCENTAGE_PROP = PREFIX + "dark_features_percentage"
NOT_VEGETATED_PERCENTAGE_PROP = PREFIX + "not_vegetated_percentage"
DEGRADED_MSI_DATA_PERCENTAGE_PROP = PREFIX + "degraded_msi_data_percentage"
HIGH_PROBA_CLOUDS_PERCENTAGE_PROP = PREFIX + "high_proba_clouds_percentage"
MEDIUM_PROBA_CLOUDS_PERCENTAGE_PROP = PREFIX + "medium_proba_clouds_percentage"
SATURATED_DEFECTIVE_PIXEL_PERCENTAGE_PROP = PREFIX + "saturated_defective_pixel_percentage"
REFLECTANCE_CONVERSION_FACTOR_PROP = PREFIX + "reflectance_conversion_factor"
MGRS_TILE_PROP = PREFIX + "mgrs_tile"

MAX_PERCENTAGE = 100
MAX_SOLAR_ANGLE = 180

PERCENTAGE_PROPS = frozenset(
    {
        WATER_PERCENTAGE_PROP,
        SNOW_ICE_PERCENTAGE_PROP,
        VEGETATION_PERCENTAGE_PROP,
        THIN_CIRRUS_PERCENTAGE_PROP,
        CLOUD_SHADOW_PERCENTAGE_PROP,
        NODATA_PIXEL_PERCENTAGE_PROP,
        UNCLASSIFIED_PERCENTAGE_PROP,
        DARK_FEATURES_PERCENTAGE_PROP,
        NOT_VEGETATED_PERCENTAGE_PROP,
        DEGRADED_MSI_DATA_PERCENTAGE_PROP,
        HIGH_PROBA_CLOUDS_PERCENTAGE_PROP,
        MEDIUM_PROBA_CLOUDS_PERCENTAGE_PROP,
        SATURATED_DEFECTIVE_PIXEL_PERCENTAGE_PROP,
    }
)

PROCESSING_BASELINE_RE = re.compile(r"^\d\d\.\d\d$")
MGRS_TILE_RE = re.compile(
    r"^\d\d?[CDEFGHJKLMNPQRSTUVWX][ABCDEFGHJKLMNPQRSTUVWXYZ]"
    r"[ABCDEFGHJKLMNPQRSTUV]$"
)


def _validate_processing_baseline(value: str | None) -> str | None:
    """Check the upstream processing-baseline pattern.

    Raises:
        ValueError: If a supplied value violates the constraint.
    """
    if value is None:
        return None
    if not PROCESSING_BASELINE_RE.match(value):
        raise ValueError(f"{PROCESSING_BASELINE_PROP} must match NN.NN. Got: {value}")
    return value


def _validate_mgrs_tile(value: str | None) -> str | None:
    """Check the upstream Sentinel-2 MGRS tile pattern.

    Raises:
        ValueError: If a supplied value violates the constraint.
    """
    if value is None:
        return None
    if not MGRS_TILE_RE.match(value):
        raise ValueError(f"{MGRS_TILE_PROP} is not a valid Sentinel-2 MGRS tile: {value}")
    return value


def _validate_percentage(prop: str, value: float | None) -> float | None:
    """Check the inclusive percentage bounds.

    Raises:
        ValueError: If a supplied value violates the constraint.
    """
    if value is None:
        return None
    if not 0 <= value <= MAX_PERCENTAGE:
        raise ValueError(f"{prop} must be between 0 and 100. Got: {value}")
    return value


class Sentinel2Extension(
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[pystac.Item | pystac.Collection],
):
    """Adapt Sentinel-2 metadata stored on a PySTAC Item.

    Use ``ext()`` for Items and ``summaries()`` for Collections.
    Optional properties return ``None`` when absent; assigning ``None`` removes them.
    Deprecated fields are preserved without automatic migration.
    """

    name: Literal["s2"] = "s2"

    # Preserve the existing PySTAC-style bulk API, including positional callers.
    def apply(  # noqa: PLR0913, PLR0917
        self,
        tile_id: str | None = None,
        granule_id: str | None = None,
        datatake_id: str | None = None,
        product_uri: str | None = None,
        datastrip_id: str | None = None,
        product_type: str | None = None,
        datatake_type: str | None = None,
        generation_time: datetime | None = None,
        processing_baseline: str | None = None,
        water_percentage: float | None = None,
        mean_solar_zenith: float | None = None,
        mean_solar_azimuth: float | None = None,
        snow_ice_percentage: float | None = None,
        vegetation_percentage: float | None = None,
        thin_cirrus_percentage: float | None = None,
        cloud_shadow_percentage: float | None = None,
        nodata_pixel_percentage: float | None = None,
        unclassified_percentage: float | None = None,
        dark_features_percentage: float | None = None,
        not_vegetated_percentage: float | None = None,
        degraded_msi_data_percentage: float | None = None,
        high_proba_clouds_percentage: float | None = None,
        medium_proba_clouds_percentage: float | None = None,
        saturated_defective_pixel_percentage: float | None = None,
        reflectance_conversion_factor: float | None = None,
        mgrs_tile: str | None = None,
    ) -> None:
        """Replace all supported fields, removing omitted or ``None`` values.

        Parameters correspond to the properties of this wrapper. Use timezone-aware
        generation times and percentages in the inclusive range 0 to 100.
        Assignments are sequential; a failure can leave earlier fields changed.
        This method does not perform full JSON Schema validation.

        Raises:
            ValueError: If a percentage, solar angle, processing baseline, or
                MGRS tile fails the corresponding setter constraint.
        """
        self.tile_id = tile_id
        self.granule_id = granule_id
        self.datatake_id = datatake_id
        self.product_uri = product_uri
        self.datastrip_id = datastrip_id
        self.product_type = product_type
        self.datatake_type = datatake_type
        self.generation_time = generation_time
        self.processing_baseline = processing_baseline
        self.water_percentage = water_percentage
        self.mean_solar_zenith = mean_solar_zenith
        self.mean_solar_azimuth = mean_solar_azimuth
        self.snow_ice_percentage = snow_ice_percentage
        self.vegetation_percentage = vegetation_percentage
        self.thin_cirrus_percentage = thin_cirrus_percentage
        self.cloud_shadow_percentage = cloud_shadow_percentage
        self.nodata_pixel_percentage = nodata_pixel_percentage
        self.unclassified_percentage = unclassified_percentage
        self.dark_features_percentage = dark_features_percentage
        self.not_vegetated_percentage = not_vegetated_percentage
        self.degraded_msi_data_percentage = degraded_msi_data_percentage
        self.high_proba_clouds_percentage = high_proba_clouds_percentage
        self.medium_proba_clouds_percentage = medium_proba_clouds_percentage
        self.saturated_defective_pixel_percentage = saturated_defective_pixel_percentage
        self.reflectance_conversion_factor = reflectance_conversion_factor
        self.mgrs_tile = mgrs_tile

    def _get_str(self, prop: str) -> str | None:
        return self._get_property(prop, str)

    def _set_str(self, prop: str, value: str | None) -> None:
        self._set_property(prop, value)

    def _get_float(self, prop: str) -> float | None:
        return self._get_property(prop, float)

    def _set_float(self, prop: str, value: float | None) -> None:
        if prop in PERCENTAGE_PROPS:
            value = _validate_percentage(prop, value)
        if (
            prop in {MEAN_SOLAR_ZENITH_PROP, MEAN_SOLAR_AZIMUTH_PROP}
            and value is not None
            and not 0 <= value <= MAX_SOLAR_ANGLE
        ):
            raise ValueError(f"{prop} must be between 0 and {MAX_SOLAR_ANGLE}. Got: {value}")
        self._set_property(prop, value)

    @property
    def tile_id(self) -> str | None:
        """Identifier of the Sentinel-2 tile product."""
        return self._get_str(TILE_ID_PROP)

    @tile_id.setter
    def tile_id(self, value: str | None) -> None:
        self._set_str(TILE_ID_PROP, value)

    @property
    def granule_id(self) -> str | None:
        """Legacy granule identifier stored independently of the tile identifier. Deprecated; prefer s2:tile_id."""
        return self._get_str(GRANULE_ID_PROP)

    @granule_id.setter
    def granule_id(self, value: str | None) -> None:
        self._set_str(GRANULE_ID_PROP, value)

    @property
    def datatake_id(self) -> str | None:
        """Identifier of the acquisition datatake."""
        return self._get_str(DATATAKE_ID_PROP)

    @datatake_id.setter
    def datatake_id(self, value: str | None) -> None:
        self._set_str(DATATAKE_ID_PROP, value)

    @property
    def product_uri(self) -> str | None:
        """URI identifying the source Sentinel-2 product."""
        return self._get_str(PRODUCT_URI_PROP)

    @product_uri.setter
    def product_uri(self, value: str | None) -> None:
        self._set_str(PRODUCT_URI_PROP, value)

    @property
    def datastrip_id(self) -> str | None:
        """Identifier of the source datastrip."""
        return self._get_str(DATASTRIP_ID_PROP)

    @datastrip_id.setter
    def datastrip_id(self, value: str | None) -> None:
        self._set_str(DATASTRIP_ID_PROP, value)

    @property
    def product_type(self) -> str | None:
        """Legacy product classification. Deprecated; prefer product:type."""
        return self._get_str(PRODUCT_TYPE_PROP)

    @product_type.setter
    def product_type(self, value: str | None) -> None:
        self._set_str(PRODUCT_TYPE_PROP, value)

    @property
    def datatake_type(self) -> str | None:
        """Acquisition datatake type, such as ``INS-NOBS``."""
        return self._get_str(DATATAKE_TYPE_PROP)

    @datatake_type.setter
    def datatake_type(self, value: str | None) -> None:
        self._set_str(DATATAKE_TYPE_PROP, value)

    @property
    def generation_time(self) -> datetime | None:
        """Product generation timestamp, serialized as an RFC 3339 string. Deprecated; prefer processing:datetime."""
        return map_opt(str_to_datetime, self._get_property(GENERATION_TIME_PROP, str))

    @generation_time.setter
    def generation_time(self, value: datetime | None) -> None:
        self._set_property(GENERATION_TIME_PROP, map_opt(datetime_to_str, value))

    @property
    def processing_baseline(self) -> str | None:
        """Processing baseline matching ``NN.NN``. Deprecated; prefer processing:version."""
        return self._get_str(PROCESSING_BASELINE_PROP)

    @processing_baseline.setter
    def processing_baseline(self, value: str | None) -> None:
        self._set_property(PROCESSING_BASELINE_PROP, _validate_processing_baseline(value))

    @property
    def water_percentage(self) -> float | None:
        """Water percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(WATER_PERCENTAGE_PROP)

    @water_percentage.setter
    def water_percentage(self, value: float | None) -> None:
        self._set_float(WATER_PERCENTAGE_PROP, value)

    @property
    def mean_solar_zenith(self) -> float | None:
        """Mean solar zenith in degrees (0 to 180 in the upstream schema). Deprecated; prefer view:sun_elevation (90 minus zenith)."""
        return self._get_float(MEAN_SOLAR_ZENITH_PROP)

    @mean_solar_zenith.setter
    def mean_solar_zenith(self, value: float | None) -> None:
        self._set_float(MEAN_SOLAR_ZENITH_PROP, value)

    @property
    def mean_solar_azimuth(self) -> float | None:
        """Mean solar azimuth in degrees (0 to 180 in the upstream schema). Deprecated; prefer view:sun_azimuth."""
        return self._get_float(MEAN_SOLAR_AZIMUTH_PROP)

    @mean_solar_azimuth.setter
    def mean_solar_azimuth(self, value: float | None) -> None:
        self._set_float(MEAN_SOLAR_AZIMUTH_PROP, value)

    @property
    def snow_ice_percentage(self) -> float | None:
        """Snow ice percentage in the inclusive range 0 to 100. Deprecated; prefer eo:snow_cover."""
        return self._get_float(SNOW_ICE_PERCENTAGE_PROP)

    @snow_ice_percentage.setter
    def snow_ice_percentage(self, value: float | None) -> None:
        self._set_float(SNOW_ICE_PERCENTAGE_PROP, value)

    @property
    def vegetation_percentage(self) -> float | None:
        """Vegetation percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(VEGETATION_PERCENTAGE_PROP)

    @vegetation_percentage.setter
    def vegetation_percentage(self, value: float | None) -> None:
        self._set_float(VEGETATION_PERCENTAGE_PROP, value)

    @property
    def thin_cirrus_percentage(self) -> float | None:
        """Thin cirrus percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(THIN_CIRRUS_PERCENTAGE_PROP)

    @thin_cirrus_percentage.setter
    def thin_cirrus_percentage(self, value: float | None) -> None:
        self._set_float(THIN_CIRRUS_PERCENTAGE_PROP, value)

    @property
    def cloud_shadow_percentage(self) -> float | None:
        """Cloud shadow percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(CLOUD_SHADOW_PERCENTAGE_PROP)

    @cloud_shadow_percentage.setter
    def cloud_shadow_percentage(self, value: float | None) -> None:
        self._set_float(CLOUD_SHADOW_PERCENTAGE_PROP, value)

    @property
    def nodata_pixel_percentage(self) -> float | None:
        """Nodata pixel percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(NODATA_PIXEL_PERCENTAGE_PROP)

    @nodata_pixel_percentage.setter
    def nodata_pixel_percentage(self, value: float | None) -> None:
        self._set_float(NODATA_PIXEL_PERCENTAGE_PROP, value)

    @property
    def unclassified_percentage(self) -> float | None:
        """Unclassified percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(UNCLASSIFIED_PERCENTAGE_PROP)

    @unclassified_percentage.setter
    def unclassified_percentage(self, value: float | None) -> None:
        self._set_float(UNCLASSIFIED_PERCENTAGE_PROP, value)

    @property
    def dark_features_percentage(self) -> float | None:
        """Dark features percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(DARK_FEATURES_PERCENTAGE_PROP)

    @dark_features_percentage.setter
    def dark_features_percentage(self, value: float | None) -> None:
        self._set_float(DARK_FEATURES_PERCENTAGE_PROP, value)

    @property
    def not_vegetated_percentage(self) -> float | None:
        """Not vegetated percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(NOT_VEGETATED_PERCENTAGE_PROP)

    @not_vegetated_percentage.setter
    def not_vegetated_percentage(self, value: float | None) -> None:
        self._set_float(NOT_VEGETATED_PERCENTAGE_PROP, value)

    @property
    def degraded_msi_data_percentage(self) -> float | None:
        """Degraded msi data percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(DEGRADED_MSI_DATA_PERCENTAGE_PROP)

    @degraded_msi_data_percentage.setter
    def degraded_msi_data_percentage(self, value: float | None) -> None:
        self._set_float(DEGRADED_MSI_DATA_PERCENTAGE_PROP, value)

    @property
    def high_proba_clouds_percentage(self) -> float | None:
        """High proba clouds percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(HIGH_PROBA_CLOUDS_PERCENTAGE_PROP)

    @high_proba_clouds_percentage.setter
    def high_proba_clouds_percentage(self, value: float | None) -> None:
        self._set_float(HIGH_PROBA_CLOUDS_PERCENTAGE_PROP, value)

    @property
    def medium_proba_clouds_percentage(self) -> float | None:
        """Medium proba clouds percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(MEDIUM_PROBA_CLOUDS_PERCENTAGE_PROP)

    @medium_proba_clouds_percentage.setter
    def medium_proba_clouds_percentage(self, value: float | None) -> None:
        self._set_float(MEDIUM_PROBA_CLOUDS_PERCENTAGE_PROP, value)

    @property
    def saturated_defective_pixel_percentage(self) -> float | None:
        """Saturated defective pixel percentage in the inclusive range 0 to 100. Deprecated; prefer statistics."""
        return self._get_float(SATURATED_DEFECTIVE_PIXEL_PERCENTAGE_PROP)

    @saturated_defective_pixel_percentage.setter
    def saturated_defective_pixel_percentage(self, value: float | None) -> None:
        self._set_float(SATURATED_DEFECTIVE_PIXEL_PERCENTAGE_PROP, value)

    @property
    def reflectance_conversion_factor(self) -> float | None:
        """Numeric factor used for reflectance conversion."""
        return self._get_float(REFLECTANCE_CONVERSION_FACTOR_PROP)

    @reflectance_conversion_factor.setter
    def reflectance_conversion_factor(self, value: float | None) -> None:
        self._set_float(REFLECTANCE_CONVERSION_FACTOR_PROP, value)

    @property
    def mgrs_tile(self) -> str | None:
        """MGRS tile identifier matching the upstream pattern, such as ``32TQM``. Deprecated; prefer MGRS fields and grid:code."""
        return self._get_str(MGRS_TILE_PROP)

    @mgrs_tile.setter
    def mgrs_tile(self, value: str | None) -> None:
        self._set_property(MGRS_TILE_PROP, _validate_mgrs_tile(value))

    @classmethod
    def get_schema_uri(cls) -> str:
        """The versioned upstream JSON Schema identifier."""
        return SCHEMA_URI

    @classmethod
    def ext(cls, obj: T, add_if_missing: bool = False) -> Sentinel2Extension[T]:
        """Wrap an Item, optionally declaring the extension on it.

        Args:
            obj: Item whose properties will be read and mutated.
            add_if_missing: Add the schema URI if the extension is not declared.

        Raises:
            pystac.ExtensionNotImplemented: If the extension is missing and
                ``add_if_missing`` is false.
            pystac.ExtensionTypeError: If the object is not an Item.
        """
        if isinstance(obj, pystac.Item):
            cls.ensure_has_extension(obj, add_if_missing)
            return cast("Sentinel2Extension[T]", ItemSentinel2Extension(obj))
        raise pystac.ExtensionTypeError(cls._ext_error_message(obj))

    @classmethod
    def summaries(
        cls, obj: pystac.Collection, add_if_missing: bool = False
    ) -> SummariesSentinel2Extension:
        """Wrap Collection summaries, optionally declaring the extension.

        Args:
            obj: Collection whose summaries will be read and mutated.
            add_if_missing: Add the schema URI if it is not already declared.

        Raises:
            pystac.ExtensionNotImplemented: If the extension is missing and
                ``add_if_missing`` is false.
        """
        cls.ensure_has_extension(obj, add_if_missing)
        return SummariesSentinel2Extension(obj)


class ItemSentinel2Extension(Sentinel2Extension[pystac.Item]):
    """Read and mutate an Item through its existing properties mapping.

    Attributes:
        item: The wrapped Item; changes are applied directly to it.
    """

    item: pystac.Item

    def __init__(self, item: pystac.Item) -> None:
        """Bind the adapter to the Item without copying its properties."""
        self.item = item
        self.properties = item.properties

    def __repr__(self) -> str:
        return f"<ItemSentinel2Extension Item id={self.item.id}>"


class SummariesSentinel2Extension(SummariesExtension):
    """Read and replace Collection summaries without aggregating Items.

    String fields use lists, numeric fields use ranges, and generation times
    use datetime ranges. Assigning ``None`` removes a summary. Summary setters
    do not apply the Item field validators.
    """

    # PySTAC returns untyped summary contents; these casts describe the field contract.
    def _get_list(self, prop: str) -> list[str] | None:
        return cast("list[str] | None", self.summaries.get_list(prop))

    def _get_range(self, prop: str) -> RangeSummary[float] | None:
        return cast("RangeSummary[float] | None", self.summaries.get_range(prop))

    @property
    def tile_id(self) -> list[str] | None:
        """Distinct tile id values represented by the Collection."""
        return self._get_list(TILE_ID_PROP)

    @tile_id.setter
    def tile_id(self, value: list[str] | None) -> None:
        self._set_summary(TILE_ID_PROP, value)

    @property
    def granule_id(self) -> list[str] | None:
        """Distinct granule id values represented by the Collection."""
        return self._get_list(GRANULE_ID_PROP)

    @granule_id.setter
    def granule_id(self, value: list[str] | None) -> None:
        self._set_summary(GRANULE_ID_PROP, value)

    @property
    def datatake_id(self) -> list[str] | None:
        """Distinct datatake id values represented by the Collection."""
        return self._get_list(DATATAKE_ID_PROP)

    @datatake_id.setter
    def datatake_id(self, value: list[str] | None) -> None:
        self._set_summary(DATATAKE_ID_PROP, value)

    @property
    def product_uri(self) -> list[str] | None:
        """Distinct product uri values represented by the Collection."""
        return self._get_list(PRODUCT_URI_PROP)

    @product_uri.setter
    def product_uri(self, value: list[str] | None) -> None:
        self._set_summary(PRODUCT_URI_PROP, value)

    @property
    def datastrip_id(self) -> list[str] | None:
        """Distinct datastrip id values represented by the Collection."""
        return self._get_list(DATASTRIP_ID_PROP)

    @datastrip_id.setter
    def datastrip_id(self, value: list[str] | None) -> None:
        self._set_summary(DATASTRIP_ID_PROP, value)

    @property
    def product_type(self) -> list[str] | None:
        """Distinct product type values represented by the Collection."""
        return self._get_list(PRODUCT_TYPE_PROP)

    @product_type.setter
    def product_type(self, value: list[str] | None) -> None:
        self._set_summary(PRODUCT_TYPE_PROP, value)

    @property
    def datatake_type(self) -> list[str] | None:
        """Distinct datatake type values represented by the Collection."""
        return self._get_list(DATATAKE_TYPE_PROP)

    @datatake_type.setter
    def datatake_type(self, value: list[str] | None) -> None:
        self._set_summary(DATATAKE_TYPE_PROP, value)

    @property
    def generation_time(self) -> RangeSummary[datetime] | None:
        """Range of product generation timestamps represented by the Collection."""
        return map_opt(
            lambda summary: RangeSummary(
                str_to_datetime(summary.minimum), str_to_datetime(summary.maximum)
            ),
            self.summaries.get_range(GENERATION_TIME_PROP),
        )

    @generation_time.setter
    def generation_time(self, value: RangeSummary[datetime] | None) -> None:
        self._set_summary(
            GENERATION_TIME_PROP,
            map_opt(
                lambda summary: RangeSummary(
                    datetime_to_str(summary.minimum), datetime_to_str(summary.maximum)
                ),
                value,
            ),
        )

    @property
    def processing_baseline(self) -> list[str] | None:
        """Distinct processing baseline values represented by the Collection."""
        return self._get_list(PROCESSING_BASELINE_PROP)

    @processing_baseline.setter
    def processing_baseline(self, value: list[str] | None) -> None:
        self._set_summary(PROCESSING_BASELINE_PROP, value)

    @property
    def water_percentage(self) -> RangeSummary[float] | None:
        """Range of water percentage values represented by the Collection."""
        return self._get_range(WATER_PERCENTAGE_PROP)

    @water_percentage.setter
    def water_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(WATER_PERCENTAGE_PROP, value)

    @property
    def mean_solar_zenith(self) -> RangeSummary[float] | None:
        """Range of mean solar zenith values represented by the Collection."""
        return self._get_range(MEAN_SOLAR_ZENITH_PROP)

    @mean_solar_zenith.setter
    def mean_solar_zenith(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(MEAN_SOLAR_ZENITH_PROP, value)

    @property
    def mean_solar_azimuth(self) -> RangeSummary[float] | None:
        """Range of mean solar azimuth values represented by the Collection."""
        return self._get_range(MEAN_SOLAR_AZIMUTH_PROP)

    @mean_solar_azimuth.setter
    def mean_solar_azimuth(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(MEAN_SOLAR_AZIMUTH_PROP, value)

    @property
    def snow_ice_percentage(self) -> RangeSummary[float] | None:
        """Range of snow ice percentage values represented by the Collection."""
        return self._get_range(SNOW_ICE_PERCENTAGE_PROP)

    @snow_ice_percentage.setter
    def snow_ice_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(SNOW_ICE_PERCENTAGE_PROP, value)

    @property
    def vegetation_percentage(self) -> RangeSummary[float] | None:
        """Range of vegetation percentage values represented by the Collection."""
        return self._get_range(VEGETATION_PERCENTAGE_PROP)

    @vegetation_percentage.setter
    def vegetation_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(VEGETATION_PERCENTAGE_PROP, value)

    @property
    def thin_cirrus_percentage(self) -> RangeSummary[float] | None:
        """Range of thin cirrus percentage values represented by the Collection."""
        return self._get_range(THIN_CIRRUS_PERCENTAGE_PROP)

    @thin_cirrus_percentage.setter
    def thin_cirrus_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(THIN_CIRRUS_PERCENTAGE_PROP, value)

    @property
    def cloud_shadow_percentage(self) -> RangeSummary[float] | None:
        """Range of cloud shadow percentage values represented by the Collection."""
        return self._get_range(CLOUD_SHADOW_PERCENTAGE_PROP)

    @cloud_shadow_percentage.setter
    def cloud_shadow_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(CLOUD_SHADOW_PERCENTAGE_PROP, value)

    @property
    def nodata_pixel_percentage(self) -> RangeSummary[float] | None:
        """Range of nodata pixel percentage values represented by the Collection."""
        return self._get_range(NODATA_PIXEL_PERCENTAGE_PROP)

    @nodata_pixel_percentage.setter
    def nodata_pixel_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(NODATA_PIXEL_PERCENTAGE_PROP, value)

    @property
    def unclassified_percentage(self) -> RangeSummary[float] | None:
        """Range of unclassified percentage values represented by the Collection."""
        return self._get_range(UNCLASSIFIED_PERCENTAGE_PROP)

    @unclassified_percentage.setter
    def unclassified_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(UNCLASSIFIED_PERCENTAGE_PROP, value)

    @property
    def dark_features_percentage(self) -> RangeSummary[float] | None:
        """Range of dark features percentage values represented by the Collection."""
        return self._get_range(DARK_FEATURES_PERCENTAGE_PROP)

    @dark_features_percentage.setter
    def dark_features_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(DARK_FEATURES_PERCENTAGE_PROP, value)

    @property
    def not_vegetated_percentage(self) -> RangeSummary[float] | None:
        """Range of not vegetated percentage values represented by the Collection."""
        return self._get_range(NOT_VEGETATED_PERCENTAGE_PROP)

    @not_vegetated_percentage.setter
    def not_vegetated_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(NOT_VEGETATED_PERCENTAGE_PROP, value)

    @property
    def degraded_msi_data_percentage(self) -> RangeSummary[float] | None:
        """Range of degraded msi data percentage values represented by the Collection."""
        return self._get_range(DEGRADED_MSI_DATA_PERCENTAGE_PROP)

    @degraded_msi_data_percentage.setter
    def degraded_msi_data_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(DEGRADED_MSI_DATA_PERCENTAGE_PROP, value)

    @property
    def high_proba_clouds_percentage(self) -> RangeSummary[float] | None:
        """Range of high proba clouds percentage values represented by the Collection."""
        return self._get_range(HIGH_PROBA_CLOUDS_PERCENTAGE_PROP)

    @high_proba_clouds_percentage.setter
    def high_proba_clouds_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(HIGH_PROBA_CLOUDS_PERCENTAGE_PROP, value)

    @property
    def medium_proba_clouds_percentage(self) -> RangeSummary[float] | None:
        """Range of medium proba clouds percentage values represented by the Collection."""
        return self._get_range(MEDIUM_PROBA_CLOUDS_PERCENTAGE_PROP)

    @medium_proba_clouds_percentage.setter
    def medium_proba_clouds_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(MEDIUM_PROBA_CLOUDS_PERCENTAGE_PROP, value)

    @property
    def saturated_defective_pixel_percentage(self) -> RangeSummary[float] | None:
        """Range of saturated defective pixel percentage values represented by the Collection."""
        return self._get_range(SATURATED_DEFECTIVE_PIXEL_PERCENTAGE_PROP)

    @saturated_defective_pixel_percentage.setter
    def saturated_defective_pixel_percentage(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(SATURATED_DEFECTIVE_PIXEL_PERCENTAGE_PROP, value)

    @property
    def reflectance_conversion_factor(self) -> RangeSummary[float] | None:
        """Range of reflectance conversion factor values represented by the Collection."""
        return self._get_range(REFLECTANCE_CONVERSION_FACTOR_PROP)

    @reflectance_conversion_factor.setter
    def reflectance_conversion_factor(self, value: RangeSummary[float] | None) -> None:
        self._set_summary(REFLECTANCE_CONVERSION_FACTOR_PROP, value)

    @property
    def mgrs_tile(self) -> list[str] | None:
        """Distinct mgrs tile values represented by the Collection."""
        return self._get_list(MGRS_TILE_PROP)

    @mgrs_tile.setter
    def mgrs_tile(self, value: list[str] | None) -> None:
        self._set_summary(MGRS_TILE_PROP, value)


class Sentinel2ExtensionHooks(ExtensionHooks):
    """Identify legacy Sentinel-2 declarations for PySTAC migration.

    These hooks do not migrate deprecated properties into other extensions.
    """

    schema_uri: str = SCHEMA_URI
    prev_extension_ids: ClassVar[set[str]] = {"sentinel-2"}
    stac_object_types: ClassVar[set[pystac.STACObjectType]] = {
        pystac.STACObjectType.COLLECTION,
        pystac.STACObjectType.ITEM,
    }


SENTINEL2_EXTENSION_HOOKS: ExtensionHooks = Sentinel2ExtensionHooks()
