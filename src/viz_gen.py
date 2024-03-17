# %% Load libraries
import geopandas
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def prep_map_data(filepath):
    """
    Processes map data from https://team.carto.com/u/andrew/tables/andrew.us_states_hexgrid/public/map
    :param filepath: Path to map file.
    :type filepath: str
    :return: GeoDataFrame with processed map data
    :rtype: geopandas.GeoDataFrame object
    """
    us_hex_map = geopandas.read_file("../data/us_states_hexgrid.geojson")
    us_hex_map = us_hex_map.drop(columns=["bees"])
    us_hex_map["google_name"] = (
        us_hex_map["google_name"]
        .str.replace("(United States)", "")
        .str.lower()
        .str.strip()
    )
    return us_hex_map


def get_elect_college_results(nara_url, year):
    """
    Gets a specific election year's electoral college results from NARA (https://www.archives.gov/electoral-college/).
    :param nara_url: URL to the NARA electoral college results webpage.
    :type nara_url: str
    :param year: Election year of interest.
    :type year: str
    :return: DataFrame with electoral college results for the specified year.
    :rtype: pandas Dataframe
    """
    state_results = pd.read_html(f"{nara_url}/{year}")[1]
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
    col_map = {
        "State's Number of Electoral Votes": "state_votes",
        "Joseph R. Biden Jr.,  of Delaware": "biden",
        "Donald J. Trump,  of Florida": "trump",
        "Kamala D. Harris,  of California": "harris",
        "Michael R. Pence,  of Indiana": "pence",
    }
    state_results.rename(columns=col_map, inplace=True)
    return state_results


def merge_and_encode_wins(us_hex_map, state_results):
    """
    Processes election results and joins them with a geopandas map object.
    :param us_hex_map: Geopandas map of the United States.
    :type us_hex_map: Geopandas map object.
    :param state_results: Dataframe containing election results.
    :type state_results: pandas.DataFrame.
    :return: Dataframe containing U.S. geographic and election data.
    :rtype: geopandas.GeoDataFrame.
    """
    us_hex_map = us_hex_map.join(state_results, on="google_name")
    us_hex_map["biden_win"] = np.where(
        us_hex_map["biden"] > us_hex_map["trump"],
        1,
        0,
    )


def build_plot(us_hex_map, filepath):
    """
    Builds plot for election results and saves to disk.
    :param us_hex_map: Map of the United States with election data.
    :type us_hex_map: geopandas.GeoDataFrame.
    :param filepath: Destination filepath for output.
    :type filepath: str
    :return: None.
    :rtype: None.
    """
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    us_hex_map.plot("biden_win", ax=ax, cmap="coolwarm_r")

    for idx, row in us_hex_map.iterrows():
        centroid = row.geometry.centroid
        plt.text(centroid.x, centroid.y, row["iso3166_2"], ha="center", va="center")
    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(
        filepath,
        format="svg",
    )
    plt.show()


def main():
    """
    Entry point for the script.
    :return: None.
    :rtype: None.
    """
    us_hex_map = prep_map_data("../data/us_states_hexgrid.geojson")
    state_results = get_elect_college_results(
        "https://www.archives.gov/electoral-college/2020"
    )
    us_hex_map = merge_and_encode_wins(us_hex_map, state_results)
    build_plot(us_hex_map, "../website_699/ppredict/static/ppredict/2020_hexbin.svg")


if __name__ == "__main__":
    main()
