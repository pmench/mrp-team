# %% Load libraries
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# %% Prepare data
# Map data source: https://team.carto.com/u/andrew/tables/andrew.us_states_hexgrid/public/map
us_hex_map = geopandas.read_file("../data/us_states_hexgrid.geojson")
us_hex_map = us_hex_map.drop(columns=["bees"])
us_hex_map["google_name"] = (
    us_hex_map["google_name"].str.replace("(United States)", "").str.lower().str.strip()
)

# %% Get state results
state_results = pd.read_html("https://www.archives.gov/electoral-college/2020")[1]
headers = state_results.iloc[0].shift(periods=2)
headers.iloc[0] = "State"
headers.iloc[1] = "State's Number of Electoral Votes"
state_results.columns = headers
state_results = state_results.drop(state_results.index[0])
state_results.iloc[:51, 1:] = state_results.iloc[:51, 1:].replace("-", 0)
state_results["State"] = (
    state_results["State"].str.replace("*", "").str.lower().str.strip()
)
state_results.iloc[:51, 1:] = state_results.iloc[:51, 1:].astype("int")
state_results.set_index("State", inplace=True)
us_hex_map = us_hex_map.join(state_results, on="google_name")
us_hex_map["biden_win"] = np.where(
    us_hex_map["Joseph R. Biden Jr.,  of Delaware"]
    > us_hex_map["Donald J. Trump,  of Florida"],
    1,
    0,
)

# Build plot
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
us_hex_map.plot("biden_win", ax=ax, cmap="coolwarm_r")

for idx, row in us_hex_map.iterrows():
    centroid = row.geometry.centroid
    plt.text(centroid.x, centroid.y, row["iso3166_2"], ha="center", va="center")
ax.set_axis_off()
plt.tight_layout()
plt.show()
