# vim: set ts=8 sts=0 sw=8 si fenc=utf-8 noet:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================

data := ../merge/output/events.parquet
locclusters := output/location_clusters.yml
output := output/events.parquet

.PHONY: all clean

all: $(output)

clean:
	-rm -rf output/*

$(output):\
	src/match.py\
	$(data)\
	$(locclusters)
	-mkdir output
	python $< \
		--data=$(data)\
		--loc_clusters=$(locclusters)\
		--output=$@

$(locclusters):\
	src/match_locations.py\
	$(data)
	-mkdir output
	python $< \
		--input=$(data)\
		--output=$@

# done.
