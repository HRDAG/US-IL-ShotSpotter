# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

input := ../import/output/oemc_gunfire.parquet
output := output/oemc_gunfire.parquet

.PHONY: all clean

all: $(output)

clean:
	-rm output/*

$(output):\
	src/format.py\
	$(input)
	-mkdir output
	python $<\
		--input=$(input)\
		--output=$@

# done.
