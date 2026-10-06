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

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/0.2.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Offline Sentinel-2 v1.0.0 schema validation tests and a Hatch documentation environment.

### Changed

- Replaced stale Sentinel-1 documentation with Sentinel-2 examples, all 26 fields, and upstream deprecation guidance.

### Deprecated

### Removed

### Fixed

- Removed dependencies on unavailable PySTAC test fixtures and VCR markers.
- Corrected empty-extension validation expectations and enforced upstream solar-angle bounds.
- Fixed strict typing and Ruff errors while retaining the existing bulk-apply API.

### Security

### Added

## [0.2.0] - 2026-10-06

### Added

- Initial project release.

[Unreleased]: https://github.com/Terradue/pystac-ext-sentinel2/compare/0.2.0...HEAD
[0.2.0]: https://github.com/Terradue/pystac-ext-sentinel2/releases/tag/0.2.0
