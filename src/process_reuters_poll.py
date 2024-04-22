"""
This script cleans and recodes data from the following Reuters Poll:

Reuters. 2024. “Reuters/Ipsos Large Sample Survey 1: January 2024.” https://doi.org/10.25940/ROPER-31120717.
"""

import pandas as pd
import helper as utl
import numpy as np


def process_reuters_poll(poll_data, keep_all=False):

    # Clean columns
    col_rename = {
        "ppethm": "race",
        "ppgender": "gender",
        "ppreg4": "region",
        "ppstaten": "state_abb",
        "age_grp2": "age_group",
        "PARTYID": "party_id",
        "TM3155Y23": "vote_choice",
        "pppa1648": "religion",
        "edu_general": "education",
    }
    poll_data = poll_data.rename(columns=col_rename)
    for col in poll_data.columns:
        poll_data[col] = poll_data[col].str.strip().str.lower()

    vote_choices = ["joe biden (democrat)", "donald trump (republican)"]
    poll_data = poll_data[poll_data["vote_choice"].isin(vote_choices)]

    # Recode age groups
    age_condition = [
        poll_data["age_group"] == "55+",
        poll_data["age_group"] == "35 thru 54",
        poll_data["age_group"] == "18 thru 34",
    ]
    age_codes = [3, 2, 1]
    poll_data["age_group_coded"] = np.select(age_condition, age_codes, default=np.nan)
    poll_data["age_group_coded"] = poll_data["age_group_coded"].astype("category")

    # Recode gender
    gender_condition = [
        poll_data["gender"] == "male",
        poll_data["gender"] == "female",
    ]
    gender_codes = [1, 0]
    poll_data["gender_coded"] = np.select(
        gender_condition, gender_codes, default=np.nan
    )
    poll_data["gender_coded"] = poll_data["gender_coded"].astype("category")

    # Recode education
    education_condition = [
        poll_data["education"] == "no college degree",
        poll_data["education"] == "college degree or more",
    ]
    education_codes = [1, 2]
    poll_data["education_coded"] = np.select(
        education_condition, education_codes, default=np.nan
    )
    poll_data["education_coded"] = poll_data["education_coded"].astype("category")

    # Recode race
    race_condition = [
        poll_data["race"] == "white, non-hispanic",
        poll_data["race"] == "hispanic",
        poll_data["race"] == "black or african american, non-hispanic",
        poll_data["race"] == "other, non-hispanic",
        poll_data["race"] == "2+ races, non-hispanic",
    ]
    race_codes = [1, 4, 2, 9, 9]
    poll_data["race_coded"] = np.select(race_condition, race_codes, default=np.nan)
    poll_data["race_coded"] = poll_data["race_coded"].astype("category")

    # Recode state
    fips = utl.get_fips(
        "https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt"
    )
    fips["STATEFP"] = fips["STATEFP"].astype(int)
    fips = fips[fips["STATEFP"] < 57]

    poll_data["state_abb"] = poll_data["state_abb"].str.lower().str.strip()
    fips["STATE"] = fips["STATE"].str.lower().str.strip()

    merged_df = pd.merge(
        poll_data, fips, left_on="state_abb", right_on="STATE", how="left"
    )
    poll_data = merged_df.drop(columns=["STATE_NAME", "STATENS", "STATE"])
    poll_data["STATEFP"] = poll_data["STATEFP"].astype("category")

    # Recode vote choice
    vote_condition = [
        poll_data["vote_choice"] == "joe biden (democrat)",
        poll_data["vote_choice"] == "donald trump (republican)",
    ]
    vote_codes = [0, 1]
    poll_data["vote_choice_coded"] = np.select(
        vote_condition, vote_codes, default=np.nan
    )
    poll_data["vote_choice_coded"] = poll_data["vote_choice_coded"].astype("category")

    # Recode region
    region_condition = [
        poll_data["region"] == "south",
        poll_data["region"] == "west",
        poll_data["region"] == "midwest",
        poll_data["region"] == "northeast",
    ]
    region_codes = [3, 4, 2, 1]
    poll_data["region_coded"] = np.select(
        region_condition, region_codes, default=np.nan
    )
    poll_data["region_coded"] = poll_data["region_coded"].astype("category")

    # Recode party affiliation
    party_condition = [
        poll_data["party_id"] == "a democrat",
        poll_data["party_id"] == "a republican",
        poll_data["party_id"] == "an independent",
        poll_data["party_id"] == "something else",
        poll_data["party_id"] == "skipped",
    ]
    party_codes = [0, 1, 2, 3, 4]
    poll_data["party_id_coded"] = np.select(
        party_condition, party_codes, default=np.nan
    )
    poll_data["party_id_coded"] = poll_data["party_id_coded"].astype("category")

    # Recode religion
    religion_condition = [
        poll_data["religion"]
        == "evangelical or protestant christian (baptist, lutheran, methodist, presbyterian, episcopalian, "
        + "pentecostal, church of christ, etc.)",
        poll_data["religion"] == "no religion",
        poll_data["religion"] == "catholic",
        poll_data["religion"] == "other christian religion",
        poll_data["religion"] == "jewish",
        poll_data["religion"] == "the church of jesus christ of latter-day saints",
        poll_data["religion"] == "refused",
        poll_data["religion"] == "jehovah's witness",
        poll_data["religion"] == "other non-christian religion",
        poll_data["religion"] == "buddhist",
        poll_data["religion"] == "hindu",
        poll_data["religion"] == "islam/muslim",
        poll_data["religion"] == "unitarian (universalist)",
        poll_data["religion"] == "greek or russian orthodox",
    ]
    religion_codes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    poll_data["religion_coded"] = np.select(
        religion_condition, religion_codes, default=-9
    )
    poll_data["religion_coded"] = poll_data["religion_coded"].astype("category")

    if keep_all:
        return poll_data
    else:
        keep_cols = [col for col in poll_data.columns if col not in col_rename.values()]
        return poll_data[keep_cols]


def main():
    """
    Entry point for the script.
    :return: None
    :rtype: None
    """
    keep_cols = [
        "ppethm",
        "ppgender",
        "ppreg4",
        "ppstaten",
        "age_grp2",
        "PARTYID",
        "TM3155Y23",
        "pppa1648",
        "edu_general",
    ]
    # data2 = pd.read_csv(
    #     "../data/reuters_poll/2024_reuters.csv", encoding="windows-1252"
    # )
    # print("done")
    reuters_data = utl.read_and_filter_poll(
        "../data/reuters_poll/2024_reuters.csv",
        encoding="windows-1252",
        cols_to_keep=keep_cols,
    )
    # reuters_data.to_csv("../data/reuters_poll/reuters_poll_test.csv")
    for col in reuters_data.columns:
        print(reuters_data[col].value_counts())

    clean_reuters_data = process_reuters_poll(reuters_data, keep_all=True)
    clean_reuters_data.to_csv(
        "../data/reuters_poll/2024_clean_reuters_all.csv", index=False
    )
    clean_coded_reuters_data = process_reuters_poll(reuters_data, keep_all=False)
    clean_coded_reuters_data.to_csv(
        "../data/reuters_poll/2024_clean_reuters_coded.csv", index=False
    )


if __name__ == "__main__":
    main()
