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
from datetime import timedelta
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


def findcandidates(eventno, eventdate, eventloc, df):
    window = df.loc[(
        df.event_no != eventno) & (
        df.date_occurred >= eventdate - timedelta(minutes=30)) & (
        df.date_occurred <= eventdate + timedelta(minutes=30))
    ]
    timeplace = window.loc[window.location == eventloc]
    #print(f"{window.shape[0]} candidate events within +/- 30min of given datetime value.\n\
    #{timeplace.shape[0]} matching the provided block address.\n")
    if not any(timeplace): return None
    cands = timeplace.event_no.unique()
    return ",".join(cands)
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/find_candidates.log")

    events = pd.read_parquet(args.input)
    assert not events.event_no.duplicated().any()
    events.date_occurred = events.date_occurred.dt.floor('Min')
    events['candidates'] = events[['event_no', 'date_occurred', 'location']].apply(
        lambda x: findcandidates(
            eventno=x.event_no,
            eventdate=x.date_occurred,
            eventloc=x.location,
            df=events), axis=1)
    events['n_candidates'] = events.candidates.apply(
        lambda x: len(x.split(',')) if pd.notna(x) else None)
    events.to_parquet(args.output)

    logger.info('done')
# }}}

# done.
