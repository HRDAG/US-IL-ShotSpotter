# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

.PHONY: all clean

all:\
	output/oemc_mp.parquet\
	output/oemc_gunfire.parquet\
	output/oemc_sst.parquet\
	output/cpd_sst.parquet

clean:
	-rm output/*

output/oemc_mp.parquet:
	-mkdir output
	cd output && ln -sf ../../OEMC_MP/export/output/oemc-prepped.parquet

output/oemc_gunfire.parquet:
	-mkdir output
	cd output && ln -sf ../../OEMC_gunfire/export/output/oemc_gunfire.parquet

output/oemc_sst.parquet:
	-mkdir output
	cd output && ln -sf ../../OEMC_sst/export/output/oemc_sst.parquet

output/cpd_sst.parquet:
	-mkdir output
	cd output && ln -sf ../../CPD_sst/export/output/cpd_sst.parquet

# done.
