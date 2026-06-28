"""Ingest exported GeoTIFFs and produce a unified ML-ready CSV.

This script expects GeoTIFFs exported from Earth Engine with a consistent band order.
Default expected bands (in order) produced by the export pipeline:
['SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7','ST_B10','NDVI','NDWI','MNDWI','NDBI','SAVI','EVI']

Usage:
python process_exported_rasters.py --input data/raw/gee_exports/landsat9 --output data/processed/tables/landsat9_samples.csv --samples 2000
"""
import os
import glob
import argparse
import random

import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import xy


DEFAULT_BANDS = [
    'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7',
    'ST_B10', 'NDVI', 'NDWI', 'MNDWI', 'NDBI', 'SAVI', 'EVI'
]


def process_tiff(path, bands_expected, samples_per_image=2000, random_state=None):
    with rasterio.open(path) as src:
        count = src.count
        # Read all bands as masked arrays
        arrays = [src.read(i + 1, masked=True).astype('float32') for i in range(count)]
        # stack: (bands, height, width)
        stack = np.stack([a.filled(np.nan) for a in arrays], axis=0)

        # valid pixel mask (at least one non-nan across bands) — prefer requiring SR bands
        valid = ~np.isnan(stack).all(axis=0)
        rows, cols = np.where(valid)
        n = len(rows)
        if n == 0:
            return pd.DataFrame()

        rng = np.random.default_rng(random_state)
        choose = rng.choice(n, size=min(samples_per_image, n), replace=False)

        samples = []
        for idx in choose:
            r = int(rows[idx])
            c = int(cols[idx])
            lon, lat = xy(src.transform, r, c)
            vals = stack[:, r, c]
            row = {'Longitude': lon, 'Latitude': lat}
            # map available bands to expected names (if count differs, only map existing)
            for i, name in enumerate(bands_expected[:stack.shape[0]]):
                v = vals[i]
                row[name] = None if np.isnan(v) else float(v)
            samples.append(row)

        return pd.DataFrame(samples)


def main(args):
    input_dir = args.input
    output_csv = args.output
    samples_per = args.samples
    bands = args.bands if args.bands else DEFAULT_BANDS

    tifs = sorted(glob.glob(os.path.join(input_dir, '*.tif')) + glob.glob(os.path.join(input_dir, '*.tiff')))
    if not tifs:
        print('No GeoTIFFs found in', input_dir)
        return

    df_list = []
    for t in tifs:
        print('Processing', t)
        df = process_tiff(t, bands, samples_per_image=samples_per, random_state=args.seed)
        if not df.empty:
            df['source_file'] = os.path.basename(t)
            df_list.append(df)

    if not df_list:
        print('No valid samples extracted.')
        return

    out = pd.concat(df_list, ignore_index=True)
    # Drop rows where key predictors are missing (e.g., NDVI and ST_B10)
    key_cols = [col for col in ['NDVI', 'ST_B10'] if col in out.columns]
    if key_cols:
        out = out.dropna(subset=key_cols)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    out.to_csv(output_csv, index=False)
    print(f'Wrote {len(out)} samples to {output_csv}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process exported GeoTIFFs into ML-ready CSV samples')
    parser.add_argument('--input', required=True, help='Input directory containing GeoTIFFs')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--samples', type=int, default=2000, help='Samples per image')
    parser.add_argument('--bands', nargs='*', help='Optional list of band names in file order')
    parser.add_argument('--seed', type=int, default=0, help='Random seed')
    args = parser.parse_args()
    main(args)
