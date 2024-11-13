# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2023, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
import logging
import yaml
import re
import numpy as np
import pandas as pd
#}}}

# ---- support methods {{{
def get_args():
    """
    Handling for filesystem arguments like the input and output.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--hand", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
    assert Path(args.hand).exists()
    return args


def get_logger(sname, file_name=None):
    """
    Handling for the logfile to track script progress.
    """
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
    """
    Reads a yaml file and returns the contents.
    """
    with open(fname, 'r') as f:
        data = yaml.safe_load(f)
    return data


def get_condinfo(df, patt):
    """
    Computes several descriptive statistics using `df` records where `patt` appears in `init_type`. \n
    When looking for reclassifications, checks for `patt` in `init_type` but not in `fin_type`.
    """
    cond = df.init_type.str.contains(patt, na=False, flags=re.I)
    info = {}
    info['n_total'] = cond.sum()
    info['n_missing_dispatch'] = ((cond) & (df.disp_date.isna())).sum()
    info['n_disp_under_30min'] = ((cond) & (df.time_to_arrive < pd.Timedelta(minutes=30))).sum()
    info['n_disp_under_2hrs'] = ((cond) & (df.time_to_arrive < pd.Timedelta(minutes=120))).sum()
    info['n_disp_under_6hrs'] = ((cond) &( df.time_to_arrive < pd.Timedelta(minutes=360))).sum()
    info['n_priority_1A'] = ((cond) & (df.init_priority == '1A')).sum()
    info['n_priority1A_missdisp'] = ((cond) & (df.init_priority == '1A') & (df.disp_date.isna())).sum()
    info['n_priority1A_disp_under30'] = ((cond) & (df.init_priority == '1A') & (df.time_to_arrive < pd.Timedelta(minutes=30))).sum()
    info['n_reclassified'] = ((cond) & ~(df.fin_type.str.contains(patt, na=False, flags=re.I))).sum()
    return info


def find_patts(df, res):
    """
    Iterates over patterns in regular expression dictionary, `res`, and \
    returns a dictionary with descriptive stats from calling `get_condinfo()` on each pattern list.
    """
    magic = {}
    for label, pattlist in res.items():
        patt = "|".join([re.escape(v) for v in pattlist])
        info = get_condinfo(df=df, patt=patt)
        magic[label] = info
    return magic


def add_anycounts(magic, cat):
    """
    Adds counts for `any_{keyword}` from individually-keyed labels found in `res` as \
    combined totals of each computation.
    """
    magic[f'any_{cat}'] = {}
    first_label = list(magic.keys())[0]
    for calc in magic[first_label].keys():
        magic[f'any_{cat}'][calc] = sum(magic[key][calc] for key in magic.keys() if key != f'any_{cat}')
    return magic


def add_props(df, n_allevents):
    """
    Adds proportions by all events and by group total for computations derived from keyword searching.
    """
    calcs = [col.replace('n_', '') for col in df.columns]
    df['prop_all_events'] = df['n_total'] / n_allevents
    for calc in calcs:
        if calc == 'total': continue
        df[f'prop_{calc}'] = df[f'n_{calc}'] / df['n_total']
    return df


def process_res(disp_df, cat, res):
    """
    Wrapper method for steps using OEMC data, a given category of keywords, and the keyword/RE dictionary. \
    Returns a DataFrame of the resulting table.
    """
    magic = find_patts(df=disp_df, res=res)
    magic = add_anycounts(magic=magic, cat=cat)
    df = pd.DataFrame(magic).T
    df = add_props(df=df, n_allevents=disp_df.shape[0])
    return df
#}}}

# ---- main {{{
if __name__ == '__main__':
    # setup logging
    logger = get_logger(__name__, "output/search.log")

    # arg handling
    args = get_args()
    logger.info("loading data")
    oemc_disp = pd.read_parquet(args.input)
    logger.info(f'loaded {oemc_disp.shape[0]:,} rows')
    keywords = readyaml(args.hand)
    assert 'help' in keywords.keys()
    assert 'injury_report' in keywords['help'].keys()
    logger.info(f'loaded {len(keywords)} keyword/phrase groups to search for in the data')

    surveil_res, help_res, supp_res = keywords['surveil'], keywords['help'], keywords['supp']
    logger.info('calculating descriptive stats for `surveil` keyword/phrase patterns')
    surveil_df = process_res(disp_df=oemc_disp, cat='surveil', res=surveil_res)
    logger.info('calculating descriptive stats for `help` keyword/phrase patterns')
    help_df = process_res(disp_df=oemc_disp, cat='help', res=help_res)
    both = pd.concat((surveil_df, help_df))
    assert not (both[[col for col in both.columns if 'prop_' in col]] > 1).any().any()
    propcols = [col for col in both.columns if 'prop_' in col]
    for propcol in propcols:
        perccol = propcol.replace('prop_', 'perc_')
        both[perccol] = both[propcol].apply(lambda x: f"{x*100:.2f}%")

    logger.info("writing keyword results data")
    both.to_parquet(args.output)
    logger.info("done.")
#}}}

# done.
