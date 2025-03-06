# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

.PHONY: all clean

all: significance-analysis

clean:
	-rm -rf output/*

significance-analysis:
	-mkdir output
	jupyter nbconvert --to notebook --inplace --execute note/demo-data-significance.ipynb
	jupyter nbconvert --to html --template pj note/demo-data-significance.ipynb
	mv note/demo-data-significance.html output/

# done.
