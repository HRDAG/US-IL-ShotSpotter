# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

.PHONY: all data merge indicate write #match

all: write

write: indicate
	cd $@ && make

indicate: #match
	cd $@ && make

# Match task takes a couple hours to run
# recommend using outputs tracked in the repo instead
#match: merge
#	cd $@ && make

merge: data
	cd $@ && make

data:
	cd $@ && make

# done.
