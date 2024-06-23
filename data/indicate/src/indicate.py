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


def add_surveilindicators(df, surveil_res):
    copy = df.copy()
    surveil_re =[re.escape(x) for v in surveil_res.values() for x in v]
    surveil_re = "|".join(surveil_re)
    copy['surveil'] = copy.init_type.str.contains(surveil_re, na=False, flags=re.I)
    shotspotter_re = "|".join(re.escape(v) for v in surveil_res['shotspotter'])
    copy['shotspotter'] = copy.init_type.str.contains(shotspotter_re, na=False, flags=re.I)
    return copy


def add_helpindicators(df, help_res):
    copy = df.copy()
    help_re =[re.escape(x) for v in help_res.values() for x in v]
    help_re = "|".join(help_re)
    copy['help'] = copy.init_type.str.contains(help_re, na=False, flags=re.I)
    for help_key in help_res.keys():
        patt = "|".join(re.escape(v) for v in help_res[help_key])
    copy[help_key] = copy.init_type.str.contains(patt, na=False, flags=re.I)
    return copy


def add_otherindicators(df):
    copy = df.copy()
    onview_re = re.escape("(OV)") + "|" + re.escape("[OV]") + "|" + "ON[ ]*VIEW"
    copy['init_on_view'] = copy.init_type.str.contains(onview_re, na=False)
    copy['fin_on_view'] = copy.fin_type.str.contains(onview_re, na=False)
    return copy
#}}}

# ---- main {{{
if __name__ == '__main__':
    # setup logging
    logger = get_logger(__name__, "output/indicate.log")

    # arg handling
    args = get_args()
    logger.info("loading data")
    oemc_disp = pd.read_parquet(args.input)
    logger.info(f'loaded {oemc_disp.shape[0]:,} rows')
    keywords = readyaml(args.hand)
    assert 'help' in keywords.keys()
    assert 'injury_report' in keywords['help'].keys()
    logger.info(f'loaded {len(keywords)} keyword/phrase groups to search for in the data')

    # 2022 only covers Jan-Apr, might be confusing to include and more straighforward to do 4-year interval
    oemc_disp = oemc_disp.loc[oemc_disp.year_called < 2022].copy()
    surveil_res, help_res, supp_res = keywords['surveil'], keywords['help'], keywords['supp']
    oemc_disp = add_surveilindicators(df=oemc_disp, surveil_res=surveil_res)
    oemc_disp = add_helpindicators(df=oemc_disp, help_res=help_res)
    oemc_disp = add_otherindicators(df=oemc_disp)
    logger.info("writing supplemented OEMC data")
    oemc_disp.to_parquet(args.output)
    logger.info("done.")
#}}}

# done.
