#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import re
import pandas as pd
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
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


def format_datetime_full(x):
    if pd.isna(x): return None
    out = pd.to_datetime(x, format="%m/%d/%Y %H:%M:%S")
    return out


def format_raw(raw):
    copy = raw.copy()
    copy.event_no = copy.event_no.astype(str)
    datecols = [col for col in copy.columns if 'date' in col.lower()]
    for col in datecols:
        copy[col] = copy[col].apply(lambda x: x.replace('.', ":") if pd.notna(x) else None)
        copy[col] = copy[col].apply(format_datetime_full)
    copy['year_entered'] = copy.entry_date.dt.year
    return copy
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/format.log")

    oemc_gunfire = pd.read_parquet(args.input)
    oemc_gunfire = format_raw(raw=oemc_gunfire)
    oemc_gunfire.to_parquet(args.output)

    logger.info('done')
# }}}
