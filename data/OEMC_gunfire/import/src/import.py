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


def readxl(fname):
    assert 'fixed' in fname, f"\
    The original CSV contains an error where some comma-separated values are not read correctly. Use the frozen/fixed version of the csv, not {fname}."
    raw = pd.read_csv(fname, header=0, dtype={'District': str})
    rules = {
        'EventNumber': 'event_no',
        'EntryDate': 'entry_date',
        'DispatchDate': 'disp_date',
        'ClearDate': 'clear_date',
        'ClosedDate': 'close_date',
        'InitialPriority': 'init_priority',
        'FinPriority': 'fin_priority',
        'InitType': 'init_type',
        'FinalType': 'fin_type',
        'FinTypeDescription': 'fin_type_desc',
        'District': 'district_oemc',
        'Location': 'call_block_address', # not sure about that
        'ServiceLocation': 'service_block_address',
        'XCoord': 'location_x',
        'YCoord': 'location_y',
    }
    raw = raw.rename(columns=rules)
    raw['source'] = 'OEMC_gunfire_reports'
    return raw
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/import.log")

    oemc_gunfire = readxl(fname=args.input)
    oemc_gunfire.to_parquet(args.output)

    logger.info('done')
# }}}
