import pandas as pd
import helper as utl


def process_reuters_poll(poll_data):
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


if __name__ == "__main__":
    main()
