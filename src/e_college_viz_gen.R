# Adapted from https://r-graph-gallery.com/a-smooth-transition-between-chloropleth-and-cartogram.html
# using https://walker-data.com/census-r/mapping-census-data-with-r.html
library(dplyr)
library(tidyr)
library(cartogram)
library(ggplot2)
library(tweenr)
library(gganimate)
library(tigris)
library(tidycensus)
library(viridis)

# Get data
e_college <- read.csv("../data/2020_ecollege_rep.csv")
e_college %>% drop_na()

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

# Create sf data with electoral colleges votes for each state
usa_pop_carto_df <- as.data.frame(usa_pop_carto)
usa_pop_carto_df$NAME <- tolower(usa_pop_carto_df$NAME)
e_college_carto_df <- merge(usa_pop_carto_df, e_college, by.x = "NAME", by.y = "state", all.x = TRUE)
e_college_carto_df <- select(e_college_carto_df, -c(STATE, STATEFP, STATENS, STATE_NAME))
e_college_carto_df$e_votes_per_10M <- (e_college_carto_df$e_votes / e_college_carto_df$estimate) * 10000000
e_college_sf <- left_join(usa_pop_carto, e_college_carto_df, by="GEOID", suffix = c("", ".y")) %>%
  select(-ends_with(".y"))
e_college_sf <- e_college_sf[!is.na(e_college_sf$e_votes), ]
e_college_carto <- cartogram_cont(e_college_sf, weight = "e_votes_per_10M")

# Create base visualizations
jpeg(
  "../output/test_cartpop.jpg",
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
  labs(title = "How Much Power Does Your Vote Have?", subtitle = "Distortion by Population") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, family = "Montserrat", size = 10),
    plot.subtitle = element_text(hjust = 0.5, family = "Montserrat", size = 8),
    legend.text = element_text(family = "Montserrat", size = 5),
    legend.title = element_text(family = "Montserrat", size = 5)
  )

jpeg(
  "../output/test_cart_ecollege.jpg",
  width = 1000,
  height = 600,
  units = "px",
  res = 200
)

ggplot(data = e_college_carto) +
  geom_sf(aes(fill = e_votes_per_10M)) +
  scale_fill_viridis(
    option = "mako",
    name = "VOTES PER 10M" # Might need to fiddle with this as the scale changes between images
  ) +
  labs(title = "How Much Power Does Your Vote Have?", subtitle = "Distortion by Electoral College Votes") +
  theme_void() +
  theme(
    plot.title = element_text(hjust = 0.5, family = "Montserrat", size = 10),
    plot.subtitle = element_text(hjust = 0.5, family = "Montserrat", size = 8),
    legend.text = element_text(family = "Montserrat", size = 5),
    legend.title = element_text(family = "Montserrat", size = 5)
  )


dev.off()




