import csv
import logging
import smtplib

from datetime import date
from typing import Optional, Any, NamedTuple, List, Tuple, Iterator
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


def find_reminders(users: List[User], days_before=7) -> Iterator[Tuple[User, User]]:
    selected = [x for x in users if (x.birthday.upcomming() - TODAY).days <= days_before]
    for bday_user in selected:
        receivers = [x for x in users if x != bday_user]
        for to_user in receivers:
            yield to_user, bday_user


class ReminderMailer:
    smtp: smtplib.SMTP = None  # for testing purposes not initialized

    TPL = """Subject: Birthday Reminder: %(name_of_birthday_person)s's birthday on %(date)s
    Body:

    Hi %(name)s,

    This is a reminder that %(name_of_birthday_person)s will be celebrating their
    birthday on %(date)s.

    There are %(amount_of_days)s left to get a present!"""

    def send_reminders(self, users: List[User]):
        for to_user, bday_user in find_reminders(users):
            logging.getLogger(__name__).info(
                f"mailing bday reminder about {bday_user.name} {bday_user.birthday.upcomming()} to  {to_user.email}"
            )

            params = dict(
                name=to_user.name,
                name_of_birthday_person=bday_user.name,
                date=bday_user.birthday.upcomming(),
                amount_of_days=(bday_user.birthday.upcomming() - TODAY).days,
            )

            msg = self.TPL % params
            self.sendmail(from_addr="info@bla.bla", to_addrs=[to_user.email], msg=msg)

    def sendmail(self, from_addr: str, to_addrs: List[str], msg: str):
        # can be overriden

        if self.smtp is None:
            self.smtp = smtplib.SMTP("localhost")

        self.smtp.sendmail(from_addr, to_addrs, msg)


def process_data():
    ...
