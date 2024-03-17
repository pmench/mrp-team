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

print(usa_pop_carto)
print(class(usa_pop_carto))

jpeg(
  "test_cart.jpg",
  width = 1000,
  height = 600,
  units = "px",
  res = 200
)

ggplot(data = usa_pop_carto) +
  geom_sf(aes(fill = estimate)) +
  scale_fill_viridis(option = "mako", name = "POP2022") +
  theme_void()

dev.off()




