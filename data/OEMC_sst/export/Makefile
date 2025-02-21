# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

.PHONY: all clean

all: output/oemc_sst.parquet

clean:
	-rm output/*

output/oemc_sst.parquet:
	-mkdir output
	cd output && ln -sf ../../format/output/oemc_sst.parquet

# done.
