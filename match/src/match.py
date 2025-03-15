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
import networkx as nx
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
            else: row = {"location": ea, "similar_locations": copy}
            data.append(row)
    out = pd.DataFrame(data).explode('similar_locations').drop_duplicates().dropna(subset=['similar_locations']).reset_index(drop=True)
    return out


def format_eventclusters(clusters):
    data = []
    for cluster in clusters:
        for ea in cluster:
            row = {'event_no': ea, 'cluster': '|'.join(sorted(cluster))}
            data.append(row)
    out = pd.DataFrame(data).drop_duplicates().dropna(subset=['cluster']).reset_index(drop=True)
    return out


def clusterevents(df):
    copy = df[['event_no', 'date_occurred', 'location', 'similar_locations',]].copy().drop_duplicates()
    cands = pd.merge(copy, copy.drop('similar_locations', axis=1),
                     left_on='similar_locations', right_on='location',
                     how='inner', suffixes=('1','2')).drop_duplicates()
    pairs = cands.loc[(abs(cands.date_occurred1 - cands.date_occurred2) < timedelta(minutes=10)) &
                      (cands.event_no1 != cands.event_no2)]
    G = nx.from_pandas_edgelist(pairs, source='event_no1', target='event_no2')
    cc = nx.connected_components(G)
    return [set(ea) for ea in cc]
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

    logger.info('begin clustering event data')
    events.date_occurred = events.date_occurred.dt.floor('Min')
    event_clusters = clusterevents(df=events)

    logger.info('begin formatting clustered event data')
    event_clusterdf = format_eventclusters(clusters=event_clusters)

    logger.info('prepare and export data with new cluster fields')
    out = pd.merge(data, event_clusterdf, on='event_no', how='left')
    out.loc[out.cluster.isna(), 'cluster'] = out.event_no

    out['n_events'] = out.cluster.apply(
        lambda x: len(x.split('|')) if pd.notna(x) else None)

    out.to_parquet(args.output)

    logger.info('done')

# }}}

# done.
