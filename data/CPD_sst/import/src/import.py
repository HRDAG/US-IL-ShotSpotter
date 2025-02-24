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


def readxl(fname):
    raw = pd.read_excel(fname, sheet_name='Data')
    rules = {
        'Beat Assigned': 'beat_assigned',
        'Call Date': 'call_date',
        'Clear Date': 'clear_date',
        'Close Date': 'close_date',
        'Dispatch Date': 'disp_date',
        'Disposition': 'disposition',
        'District': 'district_cpd',
        'Duplicate Event': 'duplicate_event',
        'Event Number': 'event_no',
        'Final Disposition Code': 'final_disposition_code',
        'Final Type': 'fin_type',
        'Initial Type': 'init_type',
        'Location Block Address': 'call_block_address',
        'On Scene Date': 'date_onscene',
        'RD Number': 'rd',
        'Response Area': 'response_area',
        'Service Area': 'service_area',
        'Service Block Address': 'service_block_address',
        'Type Descr': 'type_descr'
    }
    raw = raw.rename(columns=rules)
    raw['source'] = 'CPD_Shotspotter_alerts'
    return raw
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/import.log")

    cpd_sst = readxl(fname=args.input)
    cpd_sst.to_parquet(args.output)

    logger.info('done')
# }}}
