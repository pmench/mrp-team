# Adapted from https://r-graph-gallery.com/a-smooth-transition-between-chloropleth-and-cartogram.html
# https://walker-data.com/census-r/mapping-census-data-with-r.html
library(dplyr)
library(cartogram)
library(ggplot2)
library(broom)
library(tweenr)
library(gganimate)
library(tigris)

usa <- states(resolution = "20m") %>%
  shift_geometry() %>%
  filter(STUSPS %in% state.abb)

jpeg(
  "test_plot_us_states.jpg",
     width = 1000,
     height = 600,
     units = "px",
     res = 200
)
plot(usa)
ggplot(data = usa) +
    geom_sf() +
    theme_void()

dev.off()




