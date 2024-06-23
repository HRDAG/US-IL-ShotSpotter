# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     TRT
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =======================================================

.PHONY: all clean

all: output/oemc_location.parquet\
	output/oemc_dispatch.parquet

clean:
	rm output/*


output/oemc_location.parquet: \
		src/import_location.R \
		input/cpd_foia221504.csv
	-mkdir output/
	Rscript --vanilla $< \
		--input=input/cpd_foia221504.csv  \
		--output=$@

output/oemc_dispatch.parquet: \
		src/import_dispatch.R \
		input/EmergencyCallTimes.csv.gz
	-mkdir output/
	Rscript --vanilla $< \
		--input=input/EmergencyCallTimes.csv.gz \
		--output=$@


# done
