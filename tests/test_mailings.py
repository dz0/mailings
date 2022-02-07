from pathlib import Path

import unittest

from pydantic import ValidationError

from mailings.core import read_csv_rows, validate_data_and_convert_into_objects, Birthday, User

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


class DataValidation(unittest.TestCase):
    """
    The data file is considered valid if:
    • it can be successfully parsed,
    • all people have a name set,
    • all people have an email set (however, you don't need to check if the email addresses are valid or not),
    • each person's birthdate is a valid date (eg. no 02-30 or 01-32) in the PAST.
    """

    def test_parse_data(self):
        data = read_csv_rows(DATA_PATH / "data.csv")

        users, errors = validate_data_and_convert_into_objects(data)
        # print(f"{users=} \n {errors=}")
        assert len(users) == 4

    def test_parse_csv_data__nonvalid(self):
        data = read_csv_rows(DATA_PATH / "data_with_errs.csv")
        users, errors = validate_data_and_convert_into_objects(data)
        # print(f"{users=} \n {errors=}")
        assert len(users) == 3  # 1) OK, 2) too many fields, 3) nonvalid email

        assert len(errors) == len(data) - len(users)
        assert len(errors) > 10
        assert {x.error.__class__.__name__ for x in errors} == {"ValueError", "ValidationError"}  # "AssertionError"

    def test_name_invalid_empty(self):
        bday = Birthday(None, "12", 29)
        with self.assertRaises(ValidationError) as cm:
            _ = User(name="", email="la@bas.lt", birthday=bday)
        print(cm.exception)
        assert "name" in str(cm.exception)
        assert "at least 1 characters" in str(cm.exception)

    def test_email_invalid_empty(self):
        bday = Birthday(None, "12", 29)
        with self.assertRaises(ValidationError) as cm:
            _ = User(name="A", email="", birthday=bday)
        print(cm.exception)
        assert "email" in str(cm.exception)
        assert "at least 1 characters" in str(cm.exception)


class BirthdayValidation(unittest.TestCase):
    def test_parse_date_3parts_ok(self):
        result = Birthday(2000, "02", 29)
        assert result.day == 29
        assert result.month == 2
        assert result.year == 2000

    def test_parse_date_2parts_ok(self):
        result = Birthday(None, "02", 29)
        print(result)

    def test_month_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            _ = Birthday(None, "13", 29)
        assert "month" in str(cm.exception)
        assert "limit_value=12" in str(cm.exception)

    def test_day_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            _ = Birthday(None, 10, 33)
        assert "day" in str(cm.exception)
        assert "limit_value=31" in str(cm.exception)

    def test_year_invalid(self):
        with self.assertRaises(ValidationError) as cm:
            _ = Birthday(2030, 10, 20)
        assert "year" in str(cm.exception)
        assert "limit_value=2022" in str(cm.exception)
