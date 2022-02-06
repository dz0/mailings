from pathlib import Path

import unittest

from mailings.core import read_csv_rows

TESTS_ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = TESTS_ROOT_DIR / "data"


class DataInput(unittest.TestCase):
    """
    The list of people will be provided in a separate text file in CSV/JSON/YAML/Other
    format (please state why you chose the other format).
    Why CSV: simplest to prepare for such (small) system -- copy/export from XLSX.

    A person's entry in the file will contain:
    1.the person's name,
    2.email,
    3.birthdate (in YYYY-MM-DD or MM-DD format).
    """

    def test_read_csv_data(self):
        data = read_csv_rows(DATA_PATH / "data.csv")
        assert len(data) == 4
        for row in data:
            assert len(row) == 3

    def test_read_csv_data__nonvalid(self):
        data = read_csv_rows(DATA_PATH / "data_with_errs.csv")
        print(data)
        assert len(data) == 15
