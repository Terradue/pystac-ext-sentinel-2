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

# Install and build

## Install the library

The package declares Python 3.10 or later and PySTAC `>=1,<2`. The test matrix covers Python 3.10–3.14.

```bash
python -m pip install pystac-ext-sentinel-2
python -c "from pystac.extensions.sentinel2 import Sentinel2Extension; print(Sentinel2Extension.get_schema_uri())"
```

## Install from a checkout

```bash
git clone https://github.com/Terradue/pystac-ext-sentinel-2.git
cd pystac-ext-sentinel-2
python -m pip install -e .
```

If an existing editable installation predates a packaging change, repeat the editable install in that environment.

## Preview the documentation

With Hatch installed, use the configured documentation environment:

```bash
hatch run docs:serve
```

Build with warnings treated as errors:

```bash
hatch run docs:build
```

## Run repository checks

With Hatch installed, run these commands from the checkout:

```bash
hatch run dev:check
hatch run dev:typecheck
hatch run dev:security
hatch run test:test
```
