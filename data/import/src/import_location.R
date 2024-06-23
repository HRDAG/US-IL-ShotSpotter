#
# Authors: TRT
# Maintainers: TS, BP
# Copyright:   2024, Invisible Institute, GPL v2 or later
# =======================================================
# US-II-MP/individual/OEMC/import/src/import_location.R

pacman::p_load(readr, arrow, logger, here, argparse, janitor)


getargs <- function() {
    parser <- argparse::ArgumentParser()

    input = here::here("individual/OEMC/import/input",
                       "cpd_foia221504.csv")
    parser$add_argument("--input", default = input)

    output = here::here("individual/OEMC/import/output", "oemc_location.parquet")
    parser$add_argument("--output", default = output)
    return(parser$parse_args())
}


getdata <- function(input) {
    location <- read_csv(input)
    location
}


main <- function() {
    log_info("run begins")

    args <- getargs()
    getdata(args$input) %>%
        clean_names() %>%
        write_parquet(args$output)

    log_info("There our nrow() run ends")
}

main()

# done.
