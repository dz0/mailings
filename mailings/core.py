import csv


def read_csv_rows(path) -> list:
    with open(path) as f:
        reader = csv.reader(f)
        return list(reader)


def process_data():
    ...
