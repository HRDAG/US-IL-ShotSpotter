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
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/subset.log")

    events = pd.read_parquet(args.input)
    assert 'area' in events.columns
    # resolve event_type data
    shotspotter = ['SST', 'PSST', 'MSST'] # keywords provided by CPD in Info sheet
    citizencalls = ['SHOTS', 'SHOTSF', 'PERSHO',] # Note: 'PERGUN', 'PERDOW','PERHLP', 'DOMBAT', etc. excluded
    events['event_type'] = 'Other'
    events['event_type'] = events.init_type.case_when([
        (events.init_type.isin(shotspotter), 'ShotSpotter alert'),
        (events.init_type.isin(citizencalls), 'Human reporting gunfire'),
    ])

    # fill in event_type description data
    eventdescs = {}
    for row in events[['fin_type', 'fin_type_desc',]].drop_duplicates().values:
        fintype = row[0]
        typedesc = row[1]
        if fintype not in eventdescs.keys(): eventdescs[fintype] = {typedesc}
        else: eventdescs[fintype].add(typedesc)
    for fintype, desclist in eventdescs.items(): eventdescs[fintype] = "|".join(sorted(eventdescs[fintype]))
    events['event_type_init'] = events.init_type.apply(lambda x: eventdescs[x] if x in eventdescs else None)
    events['event_type_fin'] = events.fin_type.apply(lambda x: eventdescs[x] if x in eventdescs else None)
    events['early_warning'] = (events.init_type == 'PERGUN') & (events.fin_type.isin(('PERSHO', 'SHOTSF')))

    # subset the data to the appropriate time period and types of events
    data = events.loc[(
        events.date_occurred >= pd.Timestamp('2021-01-01')) & (
        events.date_occurred <= pd.Timestamp('2024-11-05')) & (
        events.event_type.isin(('ShotSpotter alert', 'Human reporting gunfire'))
        )].drop_duplicates()
    assert 'area' in data.columns
    data.drop(columns=['fin_type_desc']).to_parquet(args.output)

    logger.info('done')
# }}}

# done.
