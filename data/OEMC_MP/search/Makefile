# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

.PHONY: all clean

all: output/keyphrase_magic.parquet

clean:
	rm output/*

output/keyphrase_magic.parquet: \
		src/search.py \
		../indicate/output/oemc_dispatch.parquet \
		../shared/hand/keywords.yml
	-mkdir output/
	python $< \
		--input=../indicate/output/oemc_dispatch.parquet  \
		--hand=../shared/hand/keywords.yml \
		--output=$@


# done
