#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import numpy as np
import pandas as pd
#}}}

# [Source](https://www.cbsnews.com/chicago/news/chicago-police-department-detective-areas-divisions-boundaries/)
mapper = {
    1: [2, 3, 7, 8, 9],
    2: [4, 5, 6, 22],
    3: [1, 12, 18, 19, 20, 24],
    4: [10, 11, 15],
    5: [14, 16, 17, 25]
}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--oemc_gunfire", default=None)
    parser.add_argument("--oemc_sst", default=None)
    parser.add_argument("--cpd_sst", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.oemc_gunfire).exists()
    assert Path(args.oemc_sst).exists()
    assert Path(args.cpd_sst).exists()
    return args


def getlogger(sname, file_name=None):
    logger = logging.getLogger(sname)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s " +
                                  "- %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler = logging.StreamHandler(stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def verifylocations(df):
    rawprop = (df.call_block_address == df.service_block_address).sum() / df.shape[0]
    subset = df[['service_block_address', 'call_block_address']].drop_duplicates()
    subsetprop = subset.loc[subset.service_block_address == subset.call_block_address].shape[0] / subset.shape[0]
    return rawprop >= .8 <= subsetprop


def reduce(xs):
    if xs.isna().all(): return None
    found = {v for v in xs if pd.notna(v)}
    return found.pop()


def format_district(v):
    if pd.isna(v): return None
    clean = v.replace('00', '')
    if clean[0] == '0': clean = clean[1:]
    if not clean.isdigit(): return np.nan
    return int(clean.strip())


def reduce_df(df, idcols):
    copy = df.copy()
    copy['district_raw'] = copy[['district_oemc', 'district_cpd']].apply(
        lambda x: x.district_oemc if pd.notna(x.district_oemc) else x.district_cpd, axis=1)
    copy['district'] = copy.district_raw.apply(format_district)
    for area, distlist in mapper.items():
        copy.loc[copy.district.isin(distlist), 'area'] = area
    return copy.groupby(idcols).agg({
        'date_occurred': lambda xs: reduce(xs),
        'date_dispatched': lambda xs: reduce(xs),
        'area': lambda xs: reduce(xs),
        'location': lambda xs: reduce(xs),
        'location_x': lambda xs: reduce(xs),
        'location_y': lambda xs: reduce(xs),
        'init_type': lambda xs: reduce(xs),
        'fin_type': lambda xs: reduce(xs),
        'fin_type_desc': lambda xs: reduce(xs),
        'disposition': lambda xs: reduce(xs),
        }).reset_index()
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/merge.log")

    renamer = {
        'call_date': 'date_occurred',
        'entry_date': 'date_occurred',
        'disp_date': 'date_dispatched',
        'disposition_reported': 'cpd_disposition',
        'type_descr': 'fin_type_desc',
    }
    maincols = [
        'event_no', 'date_occurred', 'init_type', 'date_dispatched',
        'district_oemc', 'district_cpd',
        'location', 'location_x', 'location_y',
        'fin_type', 'fin_type_desc', 'disposition',
    ]
    oemc_gunfire = pd.read_parquet(args.oemc_gunfire).rename(columns=renamer)
    oemc_sst = pd.read_parquet(args.oemc_sst).rename(columns=renamer)
    cpd_sst = pd.read_parquet(args.cpd_sst).rename(columns=renamer)

    full = pd.concat([oemc_gunfire, oemc_sst, cpd_sst])
    assert verifylocations(df=full)
    full.rename(columns={'service_block_address': 'location',}, inplace=True)

    less = full[maincols].drop_duplicates()
    less = reduce_df(df=less, idcols=['event_no',])
    assert not less.event_no.duplicated().any()
    assert 'area' in less.columns
    less.to_parquet(args.output)

    logger.info('done')
# }}}

# done.
