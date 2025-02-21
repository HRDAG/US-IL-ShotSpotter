# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

.PHONY:\
	all\
	clean\
	OEMC_MP\
	OEMC_gunfire\
	OEMC_sst\
	CPD_sst

all:\
	OEMC_MP\
	OEMC_gunfire\
	OEMC_sst\
	CPD_sst

clean:
	cd OEMC_MP &&  make clean
	cd OEMC_gunfire && make clean
	cd OEMC_sst && make clean
	cd CPD_sst && make clean

export:
	cd $@ && make

OEMC_MP:
	cd $@ && make

OEMC_gunfire:
	cd $@ && make

OEMC_sst:
	cd $@ && make

CPD_sst:
	cd $@ && make

# done.
