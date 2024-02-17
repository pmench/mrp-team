"""
This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau.
"""
import os

import requests

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
    :return: Requested Census data with headers
    :rtype: list of lists
    """
    key = os.getenv(api_key)
    query = f"{CENSUS_ENDPOINT}/{year}/{dataset}?get={variables}&for={geo}&key={key}"
    response = requests.get(query)
    return response


def main():
    """
    Entry point for program
    :return: None.
    :rtype: None.
    """
    var = "NAME,B02015_009E,B02015_009M"
    t = get_data("2022", "acs/acs1", "us:*", var, "CENSUS_API_KEY")
    print(t.text)


if __name__ == "__main__":
    main()
