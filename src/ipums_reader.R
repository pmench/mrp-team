library(ipumsr)
ddi <- read_ipums_ddi("data/usa_00001.xml")
data <- read_ipums_micro(ddi)