import argparse

from mailings.core import do_validate, read_csv_rows, validate_data_and_convert_into_objects, ReminderMailer

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--command", choices=["validate", "send_reminders"])
parser.add_argument("-d", "--data_path")

args = parser.parse_args()

data = read_csv_rows(args.data_path)

if args.command == "validate":
    # # instead of test:
    # # args:  -c validate -d tests/data/data_with_errs.csv
    do_validate(data)
elif args.command == "send_reminders":
    users, errors = validate_data_and_convert_into_objects(data)
    mailer = ReminderMailer()
    # mailer.smtp  # configure if needed

    # # instead of test:
    # # args:  -c send_reminders -d tests/data/data.csv
    # # monkeypatch (optionally) few things -- to see output
    # mailer.sendmail = lambda from_addr, to_addrs, msg: print(from_addr, to_addrs, msg[:100])
    # from mailings import core
    # core.TODAY = core.date(2000, 12, 31)

    mailer.send_reminders(users)
else:
    raise NotImplementedError()
