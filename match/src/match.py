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
import yaml
from datetime import timedelta
import pandas as pd
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=None)
    parser.add_argument("--loc_clusters", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.data).exists()
    assert Path(args.loc_clusters).exists()
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


def readyaml(fname):
    with open(fname, 'r') as f:
        data = yaml.safe_load(f)
    return data


def format_locclusters(clusters):
    data = []
    for cluster in clusters:
        for ea in cluster:
            if pd.isna(ea): continue
            copy = cluster.copy()
            copy.remove(ea)
            if copy == set(): row = {"location": ea, "similar_locations": None}
            else: row = {"location": ea, "similar_locations": " | ".join(copy)}
            data.append(row)
    out = pd.DataFrame(data).drop_duplicates().dropna(subset=['similar_locations']).reset_index(drop=True)
    return out


def format_eventclusters(clusters):
    data = []
    for cluster in clusters:
        for ea in cluster:
            copy = cluster.copy()
            copy.remove(ea)
            if copy == set(): row = {"event_no": ea, "candidate_events": None}
            else: row = {"event_no": ea, "candidate_events": " | ".join(copy)}
            data.append(row)
    out = pd.DataFrame(data).drop_duplicates().dropna(subset=['candidate_events']).reset_index(drop=True)
    return out


def clusterevents(df):
    copy = df[['event_no', 'date_occurred', 'location', 'similar_locations',]].copy().drop_duplicates()
    clusters = []
    seen = set()
    for tup in copy.itertuples():
        eventno = tup.event_no
        seen.add(eventno)
        cands = copy.loc[~copy.event_no.isin(seen)].copy()
        cands['similar'] = (
            cands.date_occurred >= (tup.date_occurred - timedelta(minutes=10))) & (
            cands.date_occurred <= (tup.date_occurred + timedelta(minutes=10))) & (
            cands.similar_locations.str.contains(tup.location, regex=False))
        found = cands.loc[cands.similar == True, 'event_no'].unique()
        cluster = {eventno,}
        seen.add(eventno)
        for ea in found:
            cluster.add(ea)
            seen.add(ea)
        clusters.append(cluster)
    return clusters
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/match.log")

    data = pd.read_parquet(args.data)
    loc_clusters = readyaml(fname=args.loc_clusters)
    assert len(loc_clusters) > 80000
    loc_clusterdf = format_locclusters(clusters=loc_clusters)

    events = pd.merge(data, loc_clusterdf, on='location', how='left')
    # From review, the second row has a shorter list of similar locations
    # The `location` string data has not been altered from the source material and sometimes has odd whitespace
    events = events.drop_duplicates(subset='event_no')
    assert not events.event_no.duplicated().any()
    assert data.event_no.nunique() == events.event_no.nunique()

    logger.info('begin clustering event data')
    events.date_occurred = events.date_occurred.dt.floor('Min')
    event_clusters = clusterevents(df=events)

    logger.info('begin formatting clustered event data')
    event_clusterdf = format_eventclusters(clusters=event_clusters)

    logger.info('prepare and export data with new cluster fields')
    events = pd.merge(events, event_clusterdf, on='event_no', how='left')
    events['n_candidates'] = events.candidate_events.apply(
        lambda x: len(x.split(' | ')) if pd.notna(x) else None)
    events.to_parquet(args.output)

    logger.info('done')

# }}}

# done.
