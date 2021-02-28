#!/usr/bin/env python3
import csv
import datetime
from pathlib import Path


ORIGINAL = Path('original')
CONVERTED = Path('result.csv')
CARD_NAME = 'Visa Classic'

RESULT_FIELDS = [
    "DATE", "TYPE", "CATEGORY", "NOTES", 'income',
    'outcome',  'incomeAccountName', 'outcomeAccountName'
]
TRANSFERS = {
    'Expense': '-',
    'Income': '+',
    'Transfer': 'Перевод'
}


def reader(data: Path):
    with data.open(encoding='utf-8-sig', newline='') as f:
        reader_ = csv.DictReader(f)

        for num, line in enumerate(reader_):
            if not num:
                continue

            yield line


def convert_date(date: str) -> str:
    date = datetime.datetime.strptime(date, "%m/%d/%y").date()
    return date.strftime("%d/%m/%Y")


def convert_transfer_type(transfer: str) -> str:
    return TRANSFERS.get(transfer, transfer)


def convert_account(account: str) -> str:
    if account == 'Cash':
        return 'Наличные'
    if account == 'Card':
        return CARD_NAME
    return account


def convert(line_dict: dict) -> dict:
    line_dict['DATE'] = convert_date(line_dict['DATE'])
    
    del line_dict['TAGS']
    del line_dict['CURRENCY']
    del line_dict['CURRENCY 2']
    del line_dict['AMOUNT 2']
    line_dict.pop(None, '')

    line_dict['TYPE'] = convert_transfer_type(line_dict['TYPE'])
    from_account = convert_account(line_dict.pop('FROM ACCOUNT'))
    line_dict['CATEGORY'] = convert_account(line_dict.pop('TO ACCOUNT / TO CATEGORY'))

    line_dict['income'] = line_dict['outcome'] = ''
    line_dict['incomeAccountName'] = line_dict['outcomeAccountName'] = ''

    if line_dict['TYPE'] == TRANSFERS['Income']:
        line_dict['incomeAccountName'] = from_account
        line_dict['income'] = line_dict.pop('AMOUNT')
    elif line_dict['TYPE'] == TRANSFERS['Expense']:
        line_dict['outcomeAccountName'] = from_account
        line_dict['outcome'] = line_dict.pop('AMOUNT')
    elif line_dict['TYPE'] == TRANSFERS['Transfer']:
        line_dict['income'] = line_dict['outcome'] = line_dict.pop('AMOUNT')

        line_dict['outcomeAccountName'] = from_account
        line_dict['incomeAccountName'] = line_dict['CATEGORY']

        line_dict['CATEGORY'] = ''

    return line_dict


def main(data: Path) -> None:
    with CONVERTED.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDS)
        writer.writeheader()

        for num, line in enumerate(reader(data), 1):
            line_dict = convert(line)
            writer.writerow(line_dict)

        print(f"{num} records successfully dumped")


if __name__ == "__main__":
    main(ORIGINAL)

