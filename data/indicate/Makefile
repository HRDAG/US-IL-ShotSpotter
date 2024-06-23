# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

.PHONY: all clean

all: output/oemc_dispatch.parquet

clean:
	rm output/*

output/oemc_dispatch.parquet: \
		src/indicate.py \
		../clean/output/oemc_dispatch.parquet \
		../shared/hand/keywords.yml
	-mkdir output/
	python $< \
		--input=../clean/output/oemc_dispatch.parquet  \
		--hand=../shared/hand/keywords.yml \
		--output=$@


# done
