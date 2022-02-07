import csv

from datetime import date
from typing import Optional, Any, NamedTuple
from pydantic.dataclasses import dataclass
from pydantic.types import conint, constr


def read_csv_rows(path) -> list:
    with open(path) as f:
        reader = csv.reader(f)
        return list(reader)


current_year = date.today().year


@dataclass
class Birthday:
    year: Optional[conint(ge=current_year - 100, le=current_year)]
    month: conint(ge=1, le=12)  # constrained-int https://pydantic-docs.helpmanual.io/usage/types/#constrained-types
    day: conint(ge=1, le=31)

    @classmethod
    def from_str(cls, val: str) -> "Birthday":
        parts = val.split("-")
        if len(parts) == 2:  # no year
            return Birthday(None, *parts)
        elif len(parts) == 3:
            return Birthday(*parts)
        else:
            raise ValueError(f"can't parse Birthday from {val!r}")


@dataclass
class User:
    # class User(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    email: constr(strip_whitespace=True, to_lower=True, min_length=1)
    birthday: Birthday


class ErrorInfo(NamedTuple):
    value: Any
    error: Exception


def validate_data_and_convert_into_objects(data: list):
    results = []
    errors = []
    for row in data:
        try:
            # assert len(row) >= 3, "not enough values in row to unpack"
            name, email, bday, *etc = row
            user = User(name=name, email=email, birthday=Birthday.from_str(bday))
            results.append(user)
        except Exception as e:
            errors.append(ErrorInfo(row, e))
    return results, errors


def process_data():
    ...
