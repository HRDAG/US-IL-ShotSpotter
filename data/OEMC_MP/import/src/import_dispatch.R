#
# Authors: TRT
# Maintainers: BP
# Copyright:   2024, Invisible Institute, GPL v2 or later
# =======================================================
# US-II-MP/OEMC/import/src/import_location.R

pacman::p_load(readr, arrow, logger, here, argparse,janitor, R.utils, dplyr)


getargs <- function() {
    parser <- argparse::ArgumentParser()


    input = here::here("OEMC/import/input",
                       "EmergencyCallTimes.csv.gz")
    parser$add_argument("--input", default = input)

    output = here::here("individual/OEMC/import/output", "oemc_dispatch.parquet")
    parser$add_argument("--output", default = output)
    return(parser$parse_args())
}


getdata <- function(input) {
    dispatch <- read_csv(input)
    dispatch
}


main <- function() {
    log_info("run begins")
    args <- getargs()
        getdata(args$input) %>%
        clean_names() %>%
        write_parquet(args$output) %>%
        glimpse()
    log_info("There our run ends")
}

main()

# done.
