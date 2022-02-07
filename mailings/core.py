import csv
import logging

from datetime import date
from typing import Optional, Any, NamedTuple, List
from pydantic.dataclasses import dataclass
from pydantic.types import conint, constr

logging.basicConfig(level=logging.DEBUG)

TODAY = date.today()
CURRENT_YEAR = TODAY.year


def read_csv_rows(path) -> list:
    with open(path) as f:
        reader = csv.reader(f)
        return list(reader)


@dataclass
class Birthday:
    year: Optional[conint(ge=CURRENT_YEAR - 100, le=CURRENT_YEAR)]
    month: conint(ge=1, le=12)  # constrained-int https://pydantic-docs.helpmanual.io/usage/types/#constrained-types
    day: conint(ge=1, le=31)

    def upcomming(self) -> date:
        the_year = TODAY.year
        if (self.month, self.day) <= (TODAY.month, TODAY.day):
            the_year += 1  # next year

        return date(the_year, self.month, self.day)  # fixme: potential err February 29

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


def do_validate(data: List[List[str]]):
    _, errors = validate_data_and_convert_into_objects(data)
    print(f"{len(errors)} errors out of {len(data)} records:")
    for e in errors:
        print(f"{' | '.join(e.value)}: \n  => {e.error} \n")


def find_reminders(users: List[User], days_before=7):
    selected = [x for x in users if (x.birthday.upcomming() - TODAY).days <= days_before]
    for about_user in selected:
        receivers = [x for x in users if x != about_user]
        for to_user in receivers:
            yield to_user, about_user


def process_data():
    ...
