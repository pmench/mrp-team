import geopandas
import matplotlib.pyplot as plt

# Map data source: https://team.carto.com/u/andrew/tables/andrew.us_states_hexgrid/public/map
us_hex_map = geopandas.read_file("../data/us_states_hexgrid.geojson")


# Display plot)
fig, ax = plt.subplots(1, 1)
us_hex_map.plot(ax=ax)

for idx, row in us_hex_map.iterrows():
    centroid = row.geometry.centroid
    plt.text(centroid.x, centroid.y, row["iso3166_2"], ha="center", va="center")
ax.set_axis_off()
plt.show()
