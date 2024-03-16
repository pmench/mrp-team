"""
This program retrieves data from the U.S. Census Bureau's API and performs some light cleaning for output to a CSV.

This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.
"""

import os

import pandas as pd
import requests
from tqdm import tqdm


CENSUS_ENDPOINT = "https://api.census.gov/data"


def get_data(year, dataset, geo, variables, api_key):
    """
    Given search parameters, retrieves the requested data from the Census API.
    See https://www.census.gov/content/dam/Census/data/developers/api-user-guide/api-guide.pdf
    :param year: Year of interest
    :type year: str
    :param dataset: Census dataset to query (acronym)
    :type dataset: str
    :param geo: Location(s) of interest
    :type geo: str
    :param variables: Units of data requested by assigned Census code
    :type variables: str
    :param api_key: Personal key for the Census API
    :type api_key: str
    :return: Census data with headers
    :rtype: list of lists
    """
    key = os.getenv(api_key)
    query = f"{CENSUS_ENDPOINT}/{year}/{dataset}?get={variables}&for={geo}&key={key}"
    response = requests.get(query)
    if response.status_code == 200:
        try:
            data = response.json()
            var_table = get_var_table(year, dataset)[0]
            headers = map_vars_to_names(data, var_table)
            data[0] = headers
            return data
        except ValueError as e:
            print(f"Error {e}: Response not valid JSON format")
            return None
    else:
        print(f"Error {response.status_code}")
        print("Response:", response.text)
    return response


def get_var_table(year, dataset):
    """
    Retrieves a Census variables table for a specific year from the Census website.
    :param year: Year of Census data requested
    :type year: str
    :param dataset: Dataset to retrieve data from
    :type dataset: str
    :return: Dataframes created from HTML tables on the Census website
    :rtype: list of dataframes
    """
    try:
        var_table = pd.read_html(f"{CENSUS_ENDPOINT}/{year}/{dataset}/variables.html")
        return var_table
    except ValueError as e:
        print(f"{e}, no table found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def map_vars_to_names(api_response, var_table):
    """
    Replaces Census variable codes with human-readable text for use as headers.
    :param api_response: Response object retrieved from the Census API
    :type api_response: JSON array
    :param var_table: Table of variable names as defined by the U.S. Census Bureau
    :type var_table: dataframe
    :return: List of headers
    :rtype: list
    """
    replacement_dict = pd.Series(
        var_table["Label"].values, index=var_table["Name"]
    ).to_dict()
    col_names = list(map(lambda val: replacement_dict.get(val, val), api_response[0]))
    col_names = tqdm(
        [var if not var.endswith("M") else "Margin of Error" for var in col_names],
        desc="Making human readable",
    )
    return col_names


def create_df(census_data, year):
    """
    Converts raw Census data to a properly formatted pandas dataframe.
    :param census_data: Demographic data retrieved from the Census API
    :type census_data: list of lists
    :param year: Year of the demographic data
    :type year: list of strings
    :return: Dataframe with demographic category as index and year of data as column header
    :rtype: dataframe
    """
    demographic_data = pd.DataFrame(census_data).T.set_index(0)
    demographic_data.index.name = "Demographic"
    try:
        demographic_data.columns = year
        return demographic_data
    except ValueError as e:
        print(f"{e}, column renaming failed. Reorienting dataframe...")
        demographic_data = demographic_data.T
        return demographic_data


def main():
    """
    Entry point for program
    :return: None.
    :rtype: None.
    """
    # Set query parameters
    # var = (
    #     "B01001_002E,B01001_003E,B01001_004E,B01001_005E,B01001_006E,B01001_007E,B01001_008E,B01001_009E,B01001_010E,"
    #     "B01001_011E,B01001_012E,B01001_013E,B01001_014E,B01001_015E,B01001_016E,B01001_017E,B01001_018E,B01001_019E,"
    #     "B01001_020E,B01001_021E,B01001_022E,B01001_023E,B01001_024E,B01001_025E"
    # )
    var = "NAME,B01001_001E"
    year = "2022"
    geo = "state:*"
    dataset = "acs/acs5"

    # Call Census API
    census_data = get_data(
        year=year,
        dataset=dataset,
        geo=geo,
        variables=var,
        api_key="CENSUS_API_KEY",
    )
    census_df = create_df(census_data, [year])
    census_df.to_csv(f"../data/{year}_state_pop.csv")


if __name__ == "__main__":
    main()
