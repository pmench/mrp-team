# Adapted from https://r-graph-gallery.com/a-smooth-transition-between-chloropleth-and-cartogram.html
# using https://walker-data.com/census-r/mapping-census-data-with-r.html
library(dplyr)
library(cartogram)
library(ggplot2)
library(tweenr)
library(gganimate)
library(tigris)
library(tidycensus)
library(viridis)

e_college <- read.csv("./data/2020_ecollege_rep.csv")

usa <- get_acs(
  geography = "state",
  variables = "B01001_001E",
  year = 2022,
  survey = "acs5",
  geometry = TRUE,
  resolution = "20m"
) %>%
  shift_geometry()

usa_pop_carto <- cartogram_cont(usa, "estimate")

# Need to use regex to create a new column with just the state name extracted from NAME so I can match on that
# df <- merge(x=usa_pop_carto, y=e_college, by.x="NAME", by.y="state", all.x=TRUE)
# or try matching on state ID might be a better strategy
# https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt
# print(df)

jpeg(
  "test_cart1.jpg",
  width = 1000,
  height = 600,
  units = "px",
  res = 200
)

ggplot(data = usa_pop_carto) +
  geom_sf(aes(fill = estimate)) +
  scale_fill_viridis(
    option = "mako",
    name = "POP2022 (M)" # Might need to fiddle with this as the scale changes between images
  ) +
  labs(title = "U.S. Cartogram", subtitle = "Population") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, family = "Montserrat", size = 10),
    plot.subtitle = element_text(hjust = 0.5, family = "Montserrat", size = 8),
    legend.text = element_text(family = "Montserrat", size = 5),
    legend.title = element_text(family = "Montserrat", size = 5)
  )


dev.off()




