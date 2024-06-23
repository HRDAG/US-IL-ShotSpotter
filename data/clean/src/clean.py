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
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
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


def format_district(v):
    """
    Formats the given value as a numeric district.
    - If the value includes '00', it's treated as a 4-character beat pattern and the padded zeros are removed.
    - If the first character of the value is '0', the first character is ignored.
    - If after the first two steps, the resulting value is not numeric, then a sentinel missing value is returned.
    - If after the first two steps, the resulting value is numeric, it is formated as an integer and returned.
    """
    clean = v.replace('00', '')
    if clean[0] == '0': clean = clean[1:]
    if not clean.isdigit(): return np.nan
    return int(clean.strip())


def format_eventinfo(df):
    """
    Format some of the basic event info like the unique `event_number` and the `district` reported.
    """
    assert df.shape[0] > 13000000
    copy = df.copy()
    logger.info('formatting basic event info fields')
    copy.rename(columns={'eventnumber': 'event_no'}, inplace=True)
    copy.event_no = copy.event_no.astype(int).astype(str)
    copy['dispatch_reported'] = copy.disp_date.notna()
    copy['numeric_district'] = copy.district.apply(format_district)
    copy['nonnumeric_district'] = copy.district.apply(lambda x: x if not x.isdigit() else None)
    return copy


def group_timedelta(td):
    """
    Groups the given TimeDelta value on a scale starting with under 5 minutes and \
    ending with more than 48 hours.\n
    Also groups missing and negative values.
    """
    if pd.isna(td): return 'No dispatch reported'
    elif td < pd.Timedelta(0): return 'Dispatch before call'
    elif td < pd.Timedelta(minutes=5): return 'Dispatch under 5 minutes'
    elif td < pd.Timedelta(minutes=15): return 'Dispatch under 15 minutes'
    elif td < pd.Timedelta(minutes=30): return 'Dispatch under 30 minutes'
    elif td < pd.Timedelta(minutes=60): return 'Dispatch under 1 hour'
    elif td < pd.Timedelta(minutes=120): return 'Dispatch under 2 hours'
    elif td < pd.Timedelta(minutes=360): return 'Dispatch under 6 hours'
    elif td < pd.Timedelta(days=.5): return 'Dispatch under 12 hours'
    elif td < pd.Timedelta(days=1): return 'Dispatch under 24 hours'
    elif td < pd.Timedelta(days=2): return 'Dispatch under 48 hours'
    return 'Dispatch 48 hours or later'


def format_datetime(df):
    """
    Format the datetime fields as DateTime values. Add supplementary fields like `year_called` and `time_to_arrive`.
    """
    copy = df.copy()
    datecols = [col for col in copy.columns if 'date' in col]
    for col in datecols:
        logger.info(f"formatting `{col}` as DateTime (takes a couple minutes)")
        copy[col] = pd.to_datetime(copy[col], format='mixed')
    logger.info('adding supplementary datetime columns')
    copy['day_called'] = copy.call_date.dt.date
    copy['year_called'] = copy.call_date.dt.year
    copy['year_dispatched'] = copy.disp_date.dt.year
    copy['time_to_arrive'] = copy.disp_date - copy.call_date
    copy['tta_group'] = copy.time_to_arrive.apply(group_timedelta)
    return copy
#}}}

# ---- main {{{
if __name__ == '__main__':
    # setup logging
    logger = get_logger(__name__, "output/clean.log")

    # arg handling
    args = get_args()
    logger.info("loading data")
    oemc_disp = pd.read_parquet(args.input)
    logger.info(f'loaded {oemc_disp.shape[0]:,} rows')
    oemc_disp = format_eventinfo(oemc_disp)
    oemc_disp = format_datetime(oemc_disp)
    assert oemc_disp.shape[0] > 13000000
    logger.info("writing data")
    oemc_disp.to_parquet(args.output)
    logger.info("done.")
#}}}

# done.