#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 16:54:33 2025

@author: buffetv
"""

import os
from blocking_algo import process_one_year  # replace with actual script name

year_env = os.getenv('year')
if year_env is None:
    raise ValueError("Environment variable 'year' is not set.")
try:
    year = int(year_env.strip())
except ValueError:
    raise ValueError(f"Environment variable 'year' must be an integer. Got: {year_env}")

hemisphere = 'SH'     # 'NH' or 'SH'

process_one_year(year, hemisphere)