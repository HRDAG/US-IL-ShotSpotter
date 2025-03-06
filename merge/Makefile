# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

oemc_gunfire := ../data/export/output/oemc_gunfire.parquet
oemc_sst := ../data/export/output/oemc_sst.parquet
cpd_sst := ../data/export/output/cpd_sst.parquet
merged := output/merged.parquet
subset := output/subset.parquet
located := output/locations.parquet
candidates := output/data.parquet

.PHONY: all clean

all: $(subset)

clean:
	-rm -rf output/*

$(candidates):\
	src/find_candidates.py\
	$(subset)
	python $< \
		--input=$(subset)\
		--output=$@

$(located):\
	src/locate.py\
	$(subset)
	python $< \
		--input=$(subset)\
		--output=$@

$(subset):\
	src/subset.py\
	$(merged)
	python $< \
		--input=$(merged)\
		--output=$@

$(merged):\
	src/merge.py\
	$(oemc_gunfire)\
	$(oemc_sst)\
	$(cpd_sst)
	-mkdir output
	python $< \
		--oemc_gunfire=$(oemc_gunfire)\
		--oemc_sst=$(oemc_sst)\
		--cpd_sst=$(cpd_sst)\
		--output=$@

# done.
