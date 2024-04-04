import os
import zipfile

import numpy as np
import pandas as pd

import helper as utl

"""
This script processes polling data from COMETrends surveys taken during the 2020 election.
https://cometrends.utdallas.edu/data-and-questionnaires/
"""


def extract_zipped_data(path, destination, file_ext=".csv"):
    """
    Unzips the given file and extracts filetypes matching the given extension.
    :param path: Path to the zipped file.
    :type path: str
    :param destination: Location to save the extracted files.
    :type destination: str
    :param file_ext: Type of file to extract from the compressed file.
    :type file_ext: str (default: ".csv")
    :return: List of filenames for the extracted files.
    :rtype: list
    """
    extracted_files = list()
    os.makedirs(destination, exist_ok=True)
    with zipfile.ZipFile(path, "r") as zip_ref:
        for file_info in zip_ref.infolist():
            if "__MACOSX" in file_info.filename:
                continue
            if not file_info.is_dir() and file_info.filename.endswith(file_ext):
                zip_ref.extract(file_info, destination)
                extracted_files.append(file_info.filename)
    print(f"Extracted STATA datafile from {path} to {destination}")
    return extracted_files


def read_comet_poll(path):
    """
    Reads a STATA file containing COMET data and displays summary information.
    :param path: Path to the data file.
    :type path: str
    :return: Comet polling data.
    :rtype: dataframe
    """
    comet_data = pd.read_stata(path)
    print("Data Summary\n")
    print(comet_data.info())
    print("\nSummary Stats:\n")
    print(comet_data.describe())
    return comet_data


def select_comet_data(comet_data, cols_to_keep):
    """
    Selects columns in COMET data to keep and discards the rest.
    :param comet_data: Comet
    :type comet_data:
    :param cols_to_keep:
    :type cols_to_keep:
    :return:
    :rtype:
    """
    comet_data = comet_data[cols_to_keep]
    return comet_data


def process_comet_data(comet_data, keep_all=False):
    col_rename = {
        "q3": "birth_year",
        "q4": "gender",
        "q5": "education",
        "q6": "race",
        "q6_6_text": "race_other",
        "q7": "state",
        "q10": "most_imp_issue",
        "q54": "voted_for",
        "q56": "plan_to_vote_for",
        "regnz": "region",
    }

    # Bucket and code age groups
    clean_comet_data = comet_data.rename(columns=col_rename)
    vote_choice = [
        "will vote for joe biden",
        "voted for joe biden",
        "voted for donald trump",
        "will vote for donald trump",
    ]
    clean_comet_data = clean_comet_data[
        (clean_comet_data["voted_for"].isin(vote_choice))
        | (clean_comet_data["plan_to_vote_for"].isin(vote_choice))
    ]
    clean_comet_data["birth_year"] = clean_comet_data["birth_year"].astype(int)
    age_bins = [0, 1965, 1985, 2002]
    age_encoding = [2, 1, 0]
    clean_comet_data["age_group"] = pd.cut(
        clean_comet_data["birth_year"], age_bins, right=True, labels=age_encoding
    )

    # Recode gender
    clean_comet_data["gender_coded"] = np.where(
        clean_comet_data["gender"] == "male", 1, 0
    )
    clean_comet_data["gender_coded"] = clean_comet_data["gender_coded"].astype(
        "category"
    )

    # Recode education
    ed_conditions = [
        clean_comet_data["education"] == "some high school or less",
        clean_comet_data["education"] == "high school graduate",
        clean_comet_data["education"] == "community college",
        clean_comet_data["education"] == "some university",
        clean_comet_data["education"] == "graduated university, b.a. or b.sc.",
        clean_comet_data["education"] == "graduate or professional school",
    ]
    ed_codes = [1, 1, 2, 2, 2, 2]
    clean_comet_data["education_coded"] = np.select(
        ed_conditions, ed_codes, default=np.nan
    )
    clean_comet_data["education_coded"] = clean_comet_data["education_coded"].astype("category")

    # Recode race
    race_conditions = [
        clean_comet_data["race"] == "white, non hispanic",
        clean_comet_data["race"] == "african american",
        clean_comet_data["race"] == "hispanic",
        clean_comet_data["race"] == "asian",
        clean_comet_data["race"] == "native american",
        clean_comet_data["race"] == "other - please specify",
    ]
    race_codes = [1, 2, 4, 3, 9, 9]
    clean_comet_data["race_coded"] = np.select(
        race_conditions, race_codes, default=np.nan
    )
    clean_comet_data["race_coded"] = clean_comet_data["race_coded"].astype("category")

    # Recode state
    fips = utl.get_fips(
        "https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt"
    )
    fips["STATEFP"] = fips["STATEFP"].astype(int)
    fips = fips[fips["STATEFP"] < 57]

    clean_comet_data["state"] = clean_comet_data["state"].str.lower().str.strip()
    fips["STATE_NAME"] = fips["STATE_NAME"].str.lower().str.strip()

    merged_df = pd.merge(
        clean_comet_data, fips, left_on="state", right_on="STATE_NAME", how="left"
    )
    clean_comet_data = merged_df.drop(columns=["STATE_NAME", "STATENS", "STATE"])
    clean_comet_data["STATEFP"] = clean_comet_data["STATEFP"].astype("category")

    # Recode most important issue
    issue_condition = [
        clean_comet_data["most_imp_issue"] == "education",
        clean_comet_data["most_imp_issue"] == "environment",
        clean_comet_data["most_imp_issue"] == "racism",
        clean_comet_data["most_imp_issue"] == "police violence",
        clean_comet_data["most_imp_issue"] == "health care",
        clean_comet_data["most_imp_issue"] == "immigration",
        clean_comet_data["most_imp_issue"] == "inequality in incomes & wealth",
        clean_comet_data["most_imp_issue"] == "corona virus (covid-19) pandemic",
        clean_comet_data["most_imp_issue"] == "poverty",
        clean_comet_data["most_imp_issue"] == "economy",
        clean_comet_data["most_imp_issue"] == "law & order",
        clean_comet_data["most_imp_issue"] == "unemployment",
        clean_comet_data["most_imp_issue"] == "other issue",
        clean_comet_data["most_imp_issue"] == "don't know",
    ]

    issue_codes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    clean_comet_data["issue_coded"] = np.select(issue_condition, issue_codes, default=np.nan)
    clean_comet_data["issue_coded"] = clean_comet_data["issue_coded"].astype("category")

    # Recode vote choice
    vote_condition = [
        # Biden condition
        (clean_comet_data["voted_for"].str.lower() == "voted for joe biden")
        | (
            clean_comet_data["plan_to_vote_for"].str.lower()
            == "will vote for joe biden"
        ),
        # Trump condition
        (clean_comet_data["voted_for"].str.lower() == "voted for donald trump")
        | (
            clean_comet_data["plan_to_vote_for"].str.lower()
            == "will vote for donald trump"
        ),
    ]
    vote_codes = [0, 1]
    clean_comet_data["vote_coded"] = np.select(
        vote_condition, vote_codes, default=np.nan
    )
    clean_comet_data["vote_coded"] = clean_comet_data["vote_coded"].astype("category")

    # Recode region
    region_condition = [
        clean_comet_data["region"] == "Midwest",
        clean_comet_data["region"] == "Northeast",
        clean_comet_data["region"] == "South",
        clean_comet_data["region"] == "West",
    ]
    region_codes = [2, 1, 3, 4]
    clean_comet_data["region_coded"] = np.select(
        region_condition, region_codes, default=np.nan
    )
    clean_comet_data["region_coded"] = clean_comet_data["region_coded"].astype("category")

    # Return cleaned data
    print(f"Dtypes Check:\n{clean_comet_data.dtypes}\n")
    print(f"NaNs Check:\n{clean_comet_data.isna().sum().sum()}\n")
    if keep_all:
        return clean_comet_data
    else:
        keep_cols = [
            col for col in clean_comet_data.columns if col not in col_rename.values()
        ]
        return clean_comet_data[keep_cols]


def main():
    """
    Entry point for script.
    :return: None.
    :rtype: None.
    """
    data_extracted = extract_zipped_data(
        "../data/comet_polls/prenov20.zip", "../data/comet_polls/", file_ext=".dta"
    )
    comet_data = read_comet_poll(f"../data/comet_polls/{data_extracted[0]}")
    comet_cols = [
        "q3",
        "q4",
        "q5",
        "q6",
        "q6_6_text",
        "q7",
        "q10",
        "q54",
        "q56",
        "regnz",
    ]
    comet_data = select_comet_data(comet_data, comet_cols)
    clean_comet_data = process_comet_data(comet_data, keep_all=True)
    comet_recoded = process_comet_data(comet_data, keep_all=False)
    clean_comet_data.to_csv("../data/comet_polls/clean_comet.csv", index=False)
    comet_recoded.to_csv("../data/comet_polls/comet_recoded.csv", index=False)


if __name__ == "__main__":
    main()
