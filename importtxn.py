import sys
from splitwise import Splitwise
from splitwise.expense import Expense
import csv
import time
import configparser
import getopt


sObj = None
hum_tum = None
group_id = 81526


class splitwise_config(object):
    def __init__(
        self,
        stage: str
    ):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.config = config[stage]
        self.consumer_key = self.config['consumer_key']
        self.consumer_secret = self.config['consumer_secret']
        self.api_key = self.config['api_key']


def createExpense(transaction):
    expense = Expense()
    expense.setGroupId(hum_tum.id)
    expense.setCost(transaction["Amount"])
    expense.setDescription(transaction["Description"])
    date_struct = transaction["Date"]
    expense.setDate("{}-{}-{}".format(date_struct.tm_year, date_struct.tm_mon, date_struct.tm_mday))
    expense.setSplitEqually(True)
    createdExpense, errors = sObj.createExpense(expense)
    return createdExpense


def deleteExpense(id):
    sObj.deleteExpense(id)


def read_csv(filename):
    # TODO Throw Exception
    transactions = list()
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            # Get rid of some useless fields
            row.pop("Notes")
            row.pop("Original Description")
            row.pop("Transaction Type")
            row.pop("Category")
            row.pop("Account Name")
            date_parts = row['Date'].split("/")
            if len(date_parts[2]) == 2:
                row['Date'] = time.strptime(row['Date'], "%m/%d/%y")
            else:
                row['Date'] = time.strptime(row['Date'], "%m/%d/%Y")
            if 'HumTum' in row["Labels"]:
                transactions.append(row)
            line_count += 1
        print('Processed {0} lines.'.format(line_count))
    return transactions


def get_api_obj(config: splitwise_config):
    return Splitwise(config.consumer_key, config.consumer_secret, api_key=config.api_key)


def get_transaction_filename(name):
    return "data/{}_transactions.csv".format(name)


def helper():
    print("You know nothing")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "n:")
    except getopt.GetOptError:
        sys.stderr.write(helper())
        sys.exit(2)

    name = None
    for opt, arg in opts:
        if opt == "-n":
            name = arg
        else:
            sys.stderr.write(helper())
            sys.exit(2)

    config: splitwise_config = splitwise_config(name)
    global sObj
    sObj = get_api_obj(config)
    global hum_tum
    hum_tum = sObj.getGroup(group_id)
    print(hum_tum.updated_at)

    hum_tum_transactions = read_csv(get_transaction_filename(name))
    for txn in hum_tum_transactions:
        expense = createExpense(txn)
        print(expense.__dict__)


if __name__ == "__main__":
    main(sys.argv[1:])
