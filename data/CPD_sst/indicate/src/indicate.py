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


def add_indicators(df):
    copy = df.copy()
    copy['disposition_reported'] = copy.disposition.notna()
    copy['shotspotter_original'] = copy.disposition.notna()
    copy['labeled_duplicate'] = copy.duplicate_event.apply(lambda x: True if x == 'Y' else False)
    kws = {
        'other_event': ['misc\\.inc', 'dist\\.other'],
        'gun_related': ['gun', 'murder', 'weap',],
        'other_crime': ['assault', 'criminal damage',],
    }
    kws['crime_related'] = kws['gun_related'] + kws['other_crime']
    for label, patts in kws.items():
        copy[label] = copy.disposition.str.contains("|".join(patts), flags=re.I, na=False)
    return copy
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/indicate.log")

    cpd_sst = pd.read_parquet(args.input)
    cpd_sst = add_indicators(df=cpd_sst)
    cpd_sst.to_parquet(args.output)

    logger.info('done')
# }}}
