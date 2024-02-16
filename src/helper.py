import csv
import json


def read_json(filepath, encoding='utf-8'):
    """
    Deserializes JSON object and returns a list or dictionary.
    :param filepath: (str) name of path for file.
    :param encoding: (str) name of encoding for file.
    :return: dict | list representation of JSON object.
    """
    with open(filepath, 'r', encoding=encoding) as file_obj:
        return json.load(file_obj)


def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
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
    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)


def write_csv(filepath, data, headers=None, encoding='utf-8', newline=''):
    """
    Writes data to a CSV file. Column headers are written as the first
    row of the CSV file if optional headers are specified.
    :param filepath: (str) path to file.
    :param data: (list | tuple ) data to write to CSV.
    :param headers: (list | tuple) optional header row for CSV.
    :param encoding: (str) name of encoding for file.
    :param newline: (str) replacement value for newline character
    :return: none.
    """
    with open(filepath, 'w', encoding=encoding, newline=newline) as file_obj:
        writer = csv.writer(file_obj)
        if headers:
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
        else:
            writer.writerows(data)


def read_csv_to_dicts(filepath, encoding='utf-8', newline='', delimiter=','):
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
    with open(filepath, 'r', newline=newline, encoding=encoding) as file_obj:
        data = []
        reader = csv.DictReader(file_obj, delimiter=delimiter)
        for line in reader:
            data.append(line)
        return data
