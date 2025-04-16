# Atmospheric Blocking Detection (ERA5-based)

This repository contains the main Python script for detecting atmospheric blocking events using geopotential height at 500 hPa. The detection method applies a gradient-based criterion derived from the scientific literature and is designed to run efficiently on high-performance computing clusters.

## About

The detection is based on meridional gradients of geopotential height (`Z500`), evaluated at ±15° and ±30° latitude from a central latitude (`phi_zero`). Blocking is identified when the geopotential field satisfies three specific gradient thresholds indicating a reversal of the meridional flow.

This method follows the algorithm presented in:
> **Davini et al. (2020)** — *Blocking frequency in the Northern and Southern Hemisphere: The role of resolution and model configuration*  
> [Journal of Climate, Vol. 33, Issue 23, Pages 10121–10144](https://journals.ametsoc.org/view/journals/clim/33/23/jcliD190862.xml)

The detection is performed independently for each year and hemisphere, making it highly parallelizable.

## Input Data

The code assumes input data are monthly ERA5 geopotential height files.

Each file must:
- Contain the variable `z` (geopotential)
- Have dimensions: `time`, `level`, `latitude`, `longitude`
- Include 500 hPa level (selection is performed in the script)

## Output

Each run of `process_one_year` produces a yearly NetCDF file.

This file contains a single variable:
- `blocking`: 1 where a blocking event is detected, NaN elsewhere

## Dependencies

- `xarray`
- `numpy`
- `tqdm` (for progress bars)

Tested with Python 3.6 (HPC module environment).

## Usage

This script is not meant to be run interactively. Instead, it is designed for HPC batch jobs.

To use the algorithm:
1. Import `process_one_year` from `blocking_algo.py`
2. Call it with a target year and hemisphere:

```python
from blocking_algo import process_one_year
process_one_year(1997, 'SH')
