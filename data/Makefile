# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================
# US-II-MP/individual/OEMC/Makefile

tasks := import clean indicate search export

# ---- standard {{{
.PHONY: all import clean indicate search export

all: export

# }}}

# ---- task-specific {{{
export: indicate search
	cd $@ && make

search: indicate
	cd $@ && make

indicate: clean
	cd $@ && make

clean: import
	cd $@ && make

import:
	cd $@ && make
# }}}

# done.