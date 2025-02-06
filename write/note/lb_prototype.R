# Authors: LB
# Mainrainers: LB
# Copyright:   2025, HRDAG, GPL v2 or later
# =========================================
# US-IL-ShotSpotter/write/note/lb_prototype.R 
library(arrow)
df <- read_parquet("../../data/OEMC_MP/export/output/oemc-prepped.parquet")
sub_df <- df[,c('event_no', 'district', 'numeric_district',
                'call_date', 'year_called',
                'dispatch_reported', 'disp_date',
                'time_to_dispatch', 'ttd_group', 
                'init_priority', 'init_type', 'fin_type',
                'event_group', 'event_type')]

# Converts all variables in district column into a categorical variable 
sub_df$district <- as.factor(sub_df$district)

# Creates contingency table
contingencyTable <- table(sub_df$district, sub_df$dispatch_reported)

# Chisq test 
test_results <- chisq.test(contingencyTable)

# Vector of expected Counts per cell
expectedCounts <- test_results$expected

# Test that all expectedCounts are >=5 
all(expectedCounts >= 5) 


# Identify which distract (rows) have any expected counts under 5
groupslt5 <- rownames(expectedCounts)[apply(expectedCounts, 
                                            1, 
                                            FUN = function(x) any(x<5))]
# Displays a vector of all distracts with expected count < 5
cat("Districts with expected counts < 5:\n")
print(groupslt5)

if (length(groupslt5) > 0) {
  # Create a new grouping variable (as a character then factor)
  sub_df$district_agg <- as.character(sub_df$district)
  sub_df$district_agg[sub_df$district %in% groupslt5] <- "Other"
  sub_df$district_agg <- factor(sub_df$district_agg)
  
  # Build the aggregated contingency table
  agg_contingency <- table(sub_df$district_agg, sub_df$dispatch_reported)
  cat("Aggregated contingency table:\n")
  print(agg_contingency)
  
  # Rerun the chi-square test with the aggregated table
  agg_test_results <- chisq.test(agg_contingency)
  cat("\nChi-square test results for aggregated table:\n")
  print(agg_test_results)
}
  