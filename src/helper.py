"""
This script contains helper functions to complete common tasks. By project convention, it is imported into other scripts
as `utl`.
"""

import csv
import gzip
import json
import os
import shutil
import zipfile

import pandas as pd

import map_viz_gen as mp


def read_json(filepath, encoding="utf-8"):
    """
    Deserializes JSON object and returns a list or dictionary.
    :param filepath: (str) name of path for file.
    :param encoding: (str) name of encoding for file.
    :return: dict | list representation of JSON object.
    """
    with open(filepath, "r", encoding=encoding) as file_obj:
        return json.load(file_obj)


def write_json(filepath, data, encoding="utf-8", ensure_ascii=False, indent=2):
    """
    Serializes an object as JSON.
    :param filepath: (str) name of path for file
    :param data: (dict | list) the data to be encoded as JSON and written to file.
    :param encoding: (str) name of the encoding for file.
    :param ensure_ascii: (bool) whether non-ASCII characters are printed as-is. If True, non-ASCII characters
        are escaped.
    :param indent: the number of "pretty printed" indentation spaces to apply to encoded JSON.
    :return: None.
    """
    with open(filepath, "w", encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)


def write_csv(
    filepath, data, headers=None, encoding="utf-8", newline="", replace_null="None"
):
    """
    Writes data to a CSV file. Column headers are written as the first
    row of the CSV file if optional headers are specified.
    :param replace_null: replacement value for missing data
    :type replace_null: str
    :param filepath: path to file.
    :type filepath: str
    :param data: data to write to CSV.
    :type data: list | tuple
    :param headers: optional header row for CSV.
    :type headers: list | tuple
    :param encoding: name of encoding for file.
    :type encoding str
    :param newline: replacement value for newline character
    :type newline: str
    :return: none
    """
    with open(filepath, "w", encoding=encoding, newline=newline) as file_obj:
        writer = csv.writer(file_obj)
        if headers:
            writer.writerow(
                [h if h is not None and h != "" else replace_null for h in headers]
            )
            for row in data:
                writer.writerow(
                    [
                        val if val is not None and val != "" else replace_null
                        for val in row
                    ]
                )
        else:
            writer.writerows(data)


def read_csv_to_dicts(filepath, encoding="utf-8", newline="", delimiter=","):
    """
    Given a filepath, creates a file object and returns a list of
    dictionaries that represent row values.
    :param filepath: path to file.
    :type filepath: str
    :param encoding: name of encoding used to decode file.
    :type encoding: str
    :param newline: specifies replacement value for newline character.
    :type newline: str
    :param delimiter: delimiter separating row values.
    :type delimiter: str
    :return: nested dictionaries representing csv data.
    :rtype: dict
    """
    with open(filepath, "r", newline=newline, encoding=encoding) as file_obj:
        data = []
        reader = csv.DictReader(file_obj, delimiter=delimiter)
        for line in reader:
            data.append(line)
        return data


def get_e_college_rep(url):
    """
    Reads and cleans electoral college allocation table from NARA website.
    :param url: URL to NARA webpage containing electoral college information.
    :type url: str
    :return: cleaned electoral college data.
    :rtype: dataframe
    """
    e_table = pd.read_html(url)[0]
    combo = pd.concat([e_table[0], e_table[1], e_table[2]], ignore_index=True)
    combined_df = combo.to_frame(name="ecollege_representation")
    combined_df[["state", "e_rep"]] = combined_df["ecollege_representation"].str.split(
        "-", expand=True
    )
    combined_df["e_votes"] = (
        combined_df["e_rep"].replace("votes", "", regex=True).str.strip()
    )
    combined_df["e_votes"] = pd.to_numeric(combined_df["e_votes"], errors="coerce")
    combined_df.drop(["e_rep", "ecollege_representation"], axis=1, inplace=True)
    combined_df["state"] = combined_df["state"].str.lower().str.strip()
    return combined_df


def get_fips(url, delimiter="|"):
    """
    Gets fips codes from Census documents.
    :param url: URL to Census documents containing FIPs codes.
    :type url: str
    :param delimiter: Optional delimiter used on Census website.
    :type delimiter: str
    :return: FIPs codes with matching state names data.
    :rtype: dataframe
    """
    fips = pd.read_csv(url, sep=delimiter)
    fips["STATE_NAME"] = fips["STATE_NAME"].str.lower().str.strip()
    return fips


def get_wiki_pres_elections(url, table=None, to_csv=False):
    """
    Retrieves table data from Wikipedia article on the outcomes of presidential elections by vote margins.
    :param url: URL to Wikipedia article.
    :type url: str
    :param table:
    :type table:
    :param to_csv:
    :type to_csv:
    :return:
    :rtype:
    """
    tables = pd.read_html(url)
    if table is None:
        elections = tables
    else:
        elections = tables[table]
    if not isinstance(elections, list):
        elections = [elections]
    if to_csv:
        for i, election in enumerate(elections):
            election.to_csv(f"../data/wiki_pres_data_{i}.csv", index=False)
        if len(elections) == 1:
            return elections[0]
    return elections


def read_ipums(ipums_file, mode="rb", output="../data/ipums.xml"):
    """
    Unzips gzip file from IPUMS and writes it to output.
    :param ipums_file: Path to IPUMS file.
    :type ipums_file: str
    :param mode: File mode to open the file.
    :type mode: str
    :param output: Path to output.
    :type output: str
    :return: None.
    :rtype: None.
    """
    with gzip.open(ipums_file, mode) as file_in:
        with open(output, "wb") as file_out:
            shutil.copyfileobj(file_in, file_out)


def join_pop_ecollege(pop_data, ecollege_data, cols=None):
    pop = pd.read_csv(pop_data)
    ecollege = pd.read_csv(ecollege_data)
    merge = pd.merge(pop, ecollege, left_on="state", right_on="STATEFP", how="left")
    if cols:
        merge = merge[[cols]]
    else:
        merge = merge[["NAME", "Estimate!!Total:", "STATE", "STATEFP", "e_votes"]]
    merge.columns = merge.columns.map(lambda x: x.lower())
    merge.to_csv("../data/pop_ecollege_join.csv", index=False)
    return merge


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
    print(f"Extracted {file_ext} datafile from {path} to {destination}")
    return extracted_files


def read_and_filter_poll(
    filepath, file_type="csv", encoding="utf-8", cols_to_keep=None
):
    """
    Reads in poll data from either a STATA file or CSV file and optionally filters columns.
    :param filepath: Path to the file.
    :type filepath: str
    :param file_type: Type of file, either CSV or STATA file (default: CSV).
    :type file_type: str
    :param encoding: Encoding of the file (default: utf-8).
    :type encoding: str
    :param cols_to_keep: Optional list of desired columns in output file. Default keeps all columns. (default: None)
    :type cols_to_keep: list | None
    :return: DataFrame with poll data.
    :rtype: dataframe
    """
    if file_type == "stata":
        poll_data = pd.read_stata(filepath)
    else:
        poll_data = pd.read_csv(filepath, encoding=encoding)
    if cols_to_keep is not None:
        poll_data = poll_data[cols_to_keep]
        return poll_data
    else:
        return poll_data


def main():
    # e_college_votes = get_e_college_rep(
    #     "https://www.archives.gov/electoral-college/allocation"
    # )
    # fips = get_fips(
    #     "https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt"
    # )
    # print(e_college_votes.head(3))
    # print(fips.head(3))
    # e_college_votes = pd.merge(
    #     fips, e_college_votes, how="left", left_on="STATE_NAME", right_on="state"
    # )
    #
    # e_college_votes.to_csv("../data/2020_ecollege_rep.csv", index=False)
    # join_pop_ecollege("../data/2022_state_pop.csv", "../data/2020_ecollege_rep.csv")
    state_results = mp.get_elect_college_results(
        "https://www.archives.gov/electoral-college",
        "2020",
        write_csv=True,
        csv_filepath="../data/2020_electoral_results.csv",
    )


if __name__ == "__main__":
    main()
