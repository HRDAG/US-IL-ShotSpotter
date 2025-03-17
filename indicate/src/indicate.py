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
import re
import pandas as pd
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--cpd_sst", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
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
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/indicate.log")

    data = pd.read_parquet(args.input)
    cpd_sst = pd.read_parquet(args.cpd_sst, columns=[
        'event_no', 'labeled_duplicate']).drop_duplicates()
    data = pd.merge(data, cpd_sst, on='event_no', how='left')
    assert data.shape[0] > 200000
    data['year_occurred'] = data.date_occurred.dt.year
    data['dispatch_reported'] = data.date_dispatched.notna()
    data['disposition_reported'] = data.disposition.notna()
    data['shotspotter_first'] = data.disposition.notna()
    data['misc_event'] = data.disposition.str.contains(
            "MISC.INC.", regex=False, flags=re.I)
    data['shotspotter_alert'] = data.event_type == 'ShotSpotter alert'
    data['human_caller'] = data.event_type == 'Human reporting gunfire'
    data['any_coref'] = data.cluster != data.event_no
    data.to_parquet(args.output)

    logger.info('done')
# }}}
