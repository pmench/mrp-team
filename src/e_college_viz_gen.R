# Inspired by https://r-graph-gallery.com/a-smooth-transition-between-chloropleth-and-cartogram.html
# using https://walker-data.com/census-r/mapping-census-data-with-r.html
library(dplyr)
library(tidyr)
library(cartogram)
library(ggplot2)
library(scales)
library(gganimate)
library(tigris)
library(tidycensus)
library(viridis)
library(sf)

NON_STATE_FIPS <- 57

interpolate <- function (start, end, n) {
  seq(from = start, to = end, length.out = n + 2)
}

# Get data
e_college <- read.csv("../data/2020_ecollege_rep.csv")
e_college <- e_college %>%
  mutate(STATEFP = as.numeric(STATEFP)) %>%
  filter(STATEFP < NON_STATE_FIPS)

usa <- get_acs(
  geography = "state",
  variables = "B01001_001E",
  year = 2022,
  survey = "acs5",
  geometry = TRUE,
  resolution = "20m"
) %>%
  filter(GEOID < NON_STATE_FIPS) %>%
  mutate(GEOID = as.numeric(GEOID)) %>%
  shift_geometry()

# Add geometries to ecollege data and normalize e-votes
ecollege_geo <- merge(usa, e_college, by.x = "GEOID", by.y = "STATEFP", all.x = TRUE)
ecollege_geo <- select(ecollege_geo, -c(STATE, STATENS, NAME, STATE_NAME, variable, moe))
ecollege_geo$evotes_10M <- (ecollege_geo$e_votes / ecollege_geo$estimate) * 10000000
col_position <- ncol(ecollege_geo) - 1
ecollege_geo <- ecollege_geo[, c(1:(col_position-1), ncol(ecollege_geo), col_position)]

# Interpolate values
extract_e_votes <- ecollege_geo$evotes_10M
extract_usa_pop <- ecollege_geo$estimate
interpolated_values <- mapply(interpolate, start = extract_e_votes, end = extract_usa_pop, n = 2)

# Build data for cartograms
base_df <- select(ecollege_geo, -c(estimate, e_votes, evotes_10M))

interpolated_values_df <- as.data.frame(interpolated_values)
anim_frames <- list()
for (i in 1:nrow(interpolated_values_df)) {
  row_data <- as.data.frame(t(interpolated_values_df[i, ]))
  anim_frames <- c(anim_frames, row_data)
}

### Adapted from ChatGPT ###
anim_frames <- lapply(seq_along(anim_frames), function(i) {
  transition_state <- as.data.frame(anim_frames[[i]])
  colnames(transition_state) <- "value"
  transition_state$id <- i
  return(transition_state)
})
############################

# Create cartograms
for (i in seq_along(anim_frames)) {
  anim_frames[[i]] <- bind_cols(base_df, anim_frames[[i]])
  anim_frames[[i]] <- st_as_sf(anim_frames[[i]], sf_column_name = "geometry")
  anim_frames[[i]] <- anim_frames[[i]] %>%
    cartogram_cont(weight = "value")
}

# Build animation
combined_anim_frames <- bind_rows(anim_frames)

base_plot <- ggplot(combined_anim_frames) +
  geom_sf(aes(fill = value)) +
  scale_fill_viridis(
    option = "mako",
    labels = label_number_auto()
  ) +
  labs(title = "How Much Power Does Your Vote Have?", subtitle = "Distortion Between Elecltoral College Votes and Population") +
  theme_void() +
  theme(
    text = element_text(color = "#22211d"),
    plot.title = element_text(hjust = 0.5, family = "Montserrat", size = 8),
    plot.subtitle = element_text(hjust = 0.5, family = "Montserrat", size = 5),
    legend.text = element_text(family = "Montserrat", size = 5),
    legend.title = element_text(family = "Montserrat", size = 5),
    legend.key.size = unit(0.2, "cm")
  )

animated_plot <- base_plot +
  transition_states(id) +
  labs(title = 'How Much Power Does Your Vote Have?',
       subtitle = "Distortion Between Electoral College Votes (Per 10M) & Population") +
  enter_fade() +
  exit_fade()

animate(animated_plot, duration = 20, fps = 10, width = 1000, height = 800, res = 250)

anim_save("../output/ecollege_pop.gif", animation = last_animation(), dpi = 250)

# Create static visualizations
pop_carto <- cartogram_cont(last(anim_frames), weight = "value")

jpeg(
  "../output/pop_carto.jpg",
  width = 1000,
  height = 600,
  units = "px",
  res = 200
)

ggplot(data = pop_carto) +
  geom_sf(aes(fill = value)) +
  scale_fill_viridis(
    option = "mako",
    name = "Population (2022)"
  ) +
  labs(title = "How Much Power Does Your Vote Have?", subtitle = "Distortion by Population") +
  theme_void() +
  theme(
    text = element_text(color = "#22211d"),
    plot.title = element_text(hjust = 0.5, family = "Montserrat", size = 10),
    plot.subtitle = element_text(hjust = 0.5, family = "Montserrat", size = 8),
    legend.text = element_text(family = "Montserrat", size = 5),
    legend.title = element_text(family = "Montserrat", size = 5)
  )

dev.off()

ecollege_carto <- cartogram_cont(first(anim_frames), weight = "value")

jpeg(
  "../output/ecollege_carto.jpg",
  width = 1000,
  height = 600,
  units = "px",
  res = 200
)

ggplot(data = ecollege_carto) +
  geom_sf(aes(fill = value)) +
  scale_fill_viridis(
    option = "mako",
    name = "Votes per 10M"
  ) +
  labs(title = "How Much Power Does Your Vote Have?", subtitle = "Distortion by Electoral College Votes") +
  theme_void() +
  theme(
    text = element_text(color = "#22211d"),
    plot.title = element_text(hjust = 0.5, family = "Montserrat", size = 10),
    plot.subtitle = element_text(hjust = 0.5, family = "Montserrat", size = 8),
    legend.text = element_text(family = "Montserrat", size = 5),
    legend.title = element_text(family = "Montserrat", size = 5)
  )
dev.off()



