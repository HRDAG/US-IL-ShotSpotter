# -*- coding: utf-8 -*-
#  :vim ft=make:
#
# Author: PB
# Maintainer(s): PB, BP
# License: (c) HRDAG 2022, GPL v2 or newer
#
# US-II-MP/export/Makefile
# -----------------------------------------------------------

.PHONY: all clean

all: output/oemc_dispatch.parquet output/keyphrase_magic.parquet

clean:
	-rm output/*

output/oemc_dispatch.parquet:
	-mkdir output
	cd output && ln -sf ../../indicate/output/oemc_dispatch.parquet

output/keyphrase_magic.parquet:
	-mkdir output
	cd output && ln -sf ../../search/output/keyphrase_magic.parquet

# done.
