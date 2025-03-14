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
import yaml
from fuzzywuzzy import fuzz
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


def writeyaml(fname, data):
    with open(fname, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
        f.close()
    print(f'{fname} written successfully')
    return 1


def fuzzratio(l, r, thresh):
    if any([pd.isna(x) for x in (l, r)]): return 0
    rat = fuzz.ratio(l, r)
    return rat >= thresh


def clusterlocs(df, thresh):
    """Threshhold is an integer percentage."""
    copy = df[['location']].copy().drop_duplicates()
    locs = []
    seen = set()
    for loc in copy.location.unique():
        cands = copy.loc[~copy.location.isin(seen)].copy()
        cands['similar'] = cands.location.apply(
                lambda x: fuzzratio(loc, x, thresh=thresh))
        found = cands.loc[cands.similar == True, 'location'].unique()
        cluster = {loc,}
        seen.add(loc)
        for ea in found:
            cluster.add(ea)
            seen.add(ea)
        locs.append(cluster)
    return locs
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    logger = getlogger(__name__, "output/match_locations.log")

    data = pd.read_parquet(args.input)
    logger.info('begin clustering locations by string distance')
    loc_clusters = clusterlocs(data, thresh=95)
    writeyaml(fname=args.output, data=loc_clusters)
    logger.info('done')

# }}}

# done.
