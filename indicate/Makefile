# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

cpd_sst := ../data/CPD_sst/export/output/cpd_sst.parquet
input := ../match/output/events.parquet
output := output/events.parquet

.PHONY: all clean

all: $(output)

clean:
	-rm -rf output/*

$(output):\
	src/indicate.py\
	$(input)\
	$(cpd_sst)
	-mkdir output
	python $< \
		--input=$(input)\
		--cpd_sst=$(cpd_sst)\
		--output=$@

# done.
