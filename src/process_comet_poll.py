import pandas as pd
from pandas.io.stata import StataReader
import zipfile
import os


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
    clean_comet_data = comet_data.rename(columns=col_rename)
    clean_comet_data["birth_year"] = clean_comet_data["birth_year"].astype(int)
    age_bins = [0, 1965, 1985, 2002]
    age_encoding = [2, 1, 0]
    clean_comet_data["age_group"] = pd.cut(
        clean_comet_data["birth_year"], age_bins, right=True, labels=age_encoding
    )
    if keep_all:
        return clean_comet_data
    else:
        return clean_comet_data[col_rename.values()]


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
    test = process_comet_data(comet_data, keep_all=True)
    print("done")


if __name__ == "__main__":
    main()
