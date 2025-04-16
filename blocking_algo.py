#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 15:16:33 2025

@author: buffetv
"""

import xarray as xr
import numpy as np
from tqdm import tqdm

def compute_GHGS(ds, phi_zero, lambda_zero, phi_s):
    """Gradient from phi_zero to phi_s (south)."""
    z_zero = ds.sel(latitude=phi_zero, longitude=lambda_zero)
    z_s = ds.sel(latitude=phi_s, longitude=lambda_zero)
    return (z_zero - z_s) / (np.abs(phi_zero) - np.abs(phi_s))

def compute_GHGN(ds, phi_zero, lambda_zero, phi_n):
    """Gradient from phi_n to phi_zero (north)."""
    z_n = ds.sel(latitude=phi_n, longitude=lambda_zero)
    z_zero = ds.sel(latitude=phi_zero, longitude=lambda_zero)
    return (z_n - z_zero) / (np.abs(phi_n) - np.abs(phi_zero))

def compute_GHGS2(ds, phi_s, lambda_zero, phi_s2):
    """Gradient from phi_s to phi_s2 (further south)."""
    z_s = ds.sel(latitude=phi_s, longitude=lambda_zero)
    z_s2 = ds.sel(latitude=phi_s2, longitude=lambda_zero)
    return (z_s - z_s2) / (np.abs(phi_s) - np.abs(phi_s2))


def check_validity(ds, phi_zero, lambda_zero, phi_n, phi_s, phi_s2):
    try:
        GHGS = compute_GHGS(ds, phi_zero, lambda_zero, phi_s)
        GHGN = compute_GHGN(ds, phi_zero, lambda_zero, phi_n)
        GHGS2 = compute_GHGS2(ds, phi_s, lambda_zero, phi_s2)

        if (GHGS > 0) and (GHGN < -10) and (GHGS2 < -5):
            return 1
    except KeyError:
        pass
    return 0

def initialize_result_array(ds):
    return xr.DataArray(
        np.full(ds.shape, np.nan),
        dims=ds.dims,
        coords=ds.coords,
        name='validity'
    )

def process_time_step(ds, t, timestep, result, hemisphere):
    lambda_values = ds.longitude.values
    phi_values = ds.latitude.values if hemisphere == 'NH' else np.abs(ds.latitude.values)

    for phi_zero in tqdm(phi_values, desc="  φ loop", leave=False):
        phi_s = phi_zero - 15 
        phi_s2 = phi_zero - 30
        phi_n = phi_zero + 15
        
        if hemisphere == 'SH':
                # For SH, latitudes are stored as positives, but we want to select negative lats
            phi_zero = -phi_zero
            phi_s = -phi_s
            phi_s2 = -phi_s2
            phi_n = -phi_n
        else:
            phi_zero = phi_zero
            phi_s = phi_s
            phi_s2 = phi_s2
            phi_n = phi_n


        for lambda_zero in lambda_values:
            
            val = check_validity(ds.isel(time=t), phi_zero, lambda_zero, phi_n, phi_s, phi_s2)
            if val == 1:
                result.loc[dict(time=timestep, latitude=phi_zero, longitude=lambda_zero)] = val

    return result

def process_one_year(year, hemisphere):
    """Process all months for a given year and hemisphere. Save result as one NetCDF file."""
    monthly_results = []

    for month in tqdm(np.arange(1, 13), desc=f" Year {year}"):
        path = f'/.../geopotential_{year}{str(month).zfill(2)}_reanaHS.nc'
        ds = xr.open_dataset(path)['z']
        ds = ds.sel(level=500) / 9.81

        # Keep only full-degree lat/lon
        ds = ds.sel(
            latitude=ds.latitude.where(ds.latitude % 1 == 0, drop=True),
            longitude=ds.longitude.where(ds.longitude % 1 == 0, drop=True)
        )

        # Initialize monthly result
        result_month = initialize_result_array(ds)

        # Loop through time steps in this month
        for t, timestep in enumerate(tqdm(ds.time, desc=f" Month {month:02}", leave=False)):
            result_month = process_time_step(ds, t, timestep, result_month, hemisphere)

        monthly_results.append(result_month)

    # Concatenate all months along time
    full_year_result = xr.concat(monthly_results, dim="time")

    # Wrap into Dataset
    result_ds = xr.Dataset({'blocking': full_year_result})

    # Save to NetCDF
    output_path = f'/.../blocking/blocking_{year}_{hemisphere}.nc'
    result_ds.to_netcdf(output_path)
    print(f"Saved: {output_path}")
