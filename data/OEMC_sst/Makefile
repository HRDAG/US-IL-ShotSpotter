# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

.PHONY: all import format export

all: export

clean:
	cd import &&  make clean
	cd format &&  make clean
	cd export && make clean

export: format
	cd $@ && make

format: import
	cd $@ && make

import:
	cd $@ && make

# done.
