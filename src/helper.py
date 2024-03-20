import csv
import json
import pandas as pd


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
    :param url:
    :type url:
    :return:
    :rtype:
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
    fips = pd.read_csv(url, sep=delimiter)
    fips["STATE_NAME"] = fips["STATE_NAME"].str.lower().str.strip()
    return fips


def main():
    e_college_votes = get_e_college_rep(
        "https://www.archives.gov/electoral-college/allocation"
    )
    fips = get_fips(
        "https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt"
    )
    print(e_college_votes.head(3))
    print(fips.head(3))
    e_college_votes = pd.merge(
        fips, e_college_votes, how="left", left_on="STATE_NAME", right_on="state"
    )

    e_college_votes.to_csv("../data/2020_ecollege_rep.csv", index=False)


if __name__ == "__main__":
    main()
