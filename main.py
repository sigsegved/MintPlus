import csv
import sys
import getopt
import time
import prettytable


main_categories = set(['Home', 'Travel', 'Transportation', 'Dining', 'Groceries', 'Gifts', 'Misc'])

personal_categories = set(['Clothing', 'Stock investment', 'Hobbies', 'Late Fee', 'Bank Fee', 'Savings', 'India',
                           'Eyecare', 'Check', 'Investments', 'Transfer', 'Doctor', 'Mobile Phone', 'Finance Charge',
                           'Financial Advisor', 'Cash & ATM', 'Personal Care', 'Sporting Goods', 'Hair',
                           'Fees & Charges', 'Newspapers & Magazines', 'DigitSavings', 'Transfer for Cash Spending',
                           'Books', 'Arts', 'Service Fee', 'Financial', 'Gym', 'Federal Tax', 'Parking',
                           'Credit Card Payment', 'Pharmacy', 'ATM Fee', 'Tuition'])

group_categories = set(['Income', 'Uber', 'Charity', 'Music', 'Shopping', 'Reimbursement', 'Home Downpayment',
                        'Shipping', 'Toys', 'Home Insurance', 'Laundry', 'Public Transportation', 'Sports',
                        'Utilities', 'Alcohol & Bars', 'Home Improvement', 'Movies & DVDs', 'Business Services',
                        'Travel', 'Air Travel', 'Television', 'Auto & Transport', 'Gas & Fuel', 'Coffee Shops',
                        'Food & Dining', 'Rental Car & Taxi', 'Internet', 'Service & Parts', 'Home Services',
                        'Hotel', 'Auto Payment', 'Restaurants', 'Bonus', 'Pet Food & Supplies', 'Fast Food',
                        'Home', 'Groceries', 'Mortgage & Rent', 'Amusement', 'Paycheck', 'Hide from Budgets & Trends',
                        'Electronics & Software', 'Interest Income', 'Furnishings', 'Spa & Massage', 'Advertising',
                        'Vacation', 'Gift', 'Health & Fitness', 'Uncategorized', 'Dentist', 'Entertainment',
                        'Misc Expenses', 'Auto Insurance'])

category_groups = dict()
category_groups['For Home'] = set(['HOA Dues', 'Home Supplies', 'Bills & Utilities', 'Home Services',
                                   'Home Downpayment', 'Shipping', 'Home Insurance', 'Laundry', 'Utilities',
                                   'Home Improvement', 'Internet', 'Service & Parts', 'Home', 'Mortgage & Rent',
                                   'Furnishings'])

category_groups['For Travel'] = set(['Travel', 'Air Travel', 'Rental Car & Taxi', 'Hotel', 'Vacation'])

category_groups['For Transportation'] = set(['Taxi', 'Auto & Transport', 'Gas & Fuel', 'Auto Payment',
                                             'Auto Insurance', 'Uber', 'Public Transportation'])

category_groups['For Dining'] = set(['Lunch', 'Uber Eats', 'Food Delivery', 'Alcohol & Bars', 'Coffee Shops',
                                     'Food & Dining', 'Restaurants', 'Fast Food'])

category_groups['For Groceries'] = set(['Groceries'])

category_groups['For Gifts'] = set(['Charity', 'Gift'])

category_groups['For Misc'] = set(['Shopping', 'Music', 'Reimbursement', 'Toys', 'Sports', 'Movies & DVDs',
                                   'Business Services', 'Television', 'Bonus', 'Pet Food & Supplies', 'Amusement',
                                   'Electronics & Software', 'Spa & Massage', 'Advertising', 'Health & Fitness',
                                   'Uncategorized', 'Dentist', 'Entertainment', 'Misc Expenses'])

category_groups['To Income'] = set(['Income', 'Paycheck', 'Salary'])


def helper():
    message = 'Usage: MintPlus -p <Path> -n <Names>\n'
    message += '\t -p : Base Path where the csv file exist\n'
    message += '\t -n : Name of people whose accounts are being consolidated\n'
    message += '\t      There should be a file for every name provided here under the base path.\n'
    message += '\t      For ex : MintPlus -p /tmp/ -n tom,ana should have two files /tmp/tom.csv and /tmp/ana.csv \n'
    message += '\t -s : Start date of the report date in MM/DD/YYYY format. \n'
    message += '\t -e : End date of the report date in MM/DD/YYYY format. \n'
    return message


def read_csv(filename, categories):
    # TODO Throw Exception
    transactions = list()
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                categories.add(row["Category"])
                # Get rid of some useless fields
                if "Vacation" in row["Labels"].split(",") and row['Category'] not in category_groups['For Travel']:
                    row['Category'] = 'Vacation'
                row.pop("Labels")
                row.pop("Notes")
                row.pop("Original Description")
                date_parts = row['Date'].split("/")
                if len(date_parts[2]) == 2:
                    row['Date'] = time.strptime(row['Date'], "%m/%d/%y")
                else:
                    row['Date'] = time.strptime(row['Date'], "%m/%d/%Y")
                transactions.append(row)
            line_count += 1
        print('Processed {0} lines.'.format(line_count))
    return transactions


# Finds if the given date in the format MM/DD/YYYY is in the given range.
def is_date_in_ranage(date, start_date, end_date):
    return (date >= start_date) & (date <= end_date)


def get_category_group(category):
    for group in category_groups.keys():
        if category in category_groups[group]:
            return group
    return None


# Date, Description, Category, Amount
def filter_transactions(transactions, start_date, end_date):
    filtered_transactions = dict()
    grouped_transactions = dict()

    for name in transactions.keys():
        grouped_transactions[name] = dict()
        filtered_transactions[name] = list()

        for group in category_groups.keys():
            grouped_transactions[name][group] = list()

        for row in transactions[name]:
            if not is_date_in_ranage(row['Date'], start_date, end_date):
                continue
            if row['Category'] == 'Uber' and float(row['Amount']) > 10.0:
                row['Category'] = 'Uber Eats'
            if row['Category'] in personal_categories:
                row['Personal'] = True
                row['Group'] = 'Personal'
            else:
                row['Personal'] = False
                group = get_category_group(row['Category'])
                if group not in grouped_transactions[name].keys():
                    grouped_transactions[name][group] = list()
                grouped_transactions[name][group].append(row)
                row['Group'] = group

            filtered_transactions[name].append(row)

    return filtered_transactions, grouped_transactions


def summarize(grouped_transactions):
    expenses = dict()
    common_expenses = dict()
    for name in grouped_transactions.keys():
        expenses[name] = dict()
        print("======== Summary for {0} ========".format(name))
        for group in grouped_transactions[name].keys():
            if group not in expenses[name].keys():
                expenses[name][group] = dict()
            total = 0
            count = 0
            for transaction in grouped_transactions[name][group]:
                sub_category = transaction['Category']
                if sub_category not in expenses[name][group].keys():
                    expenses[name][group][sub_category] = {'Count': 0, 'Total': 0}
                expenses[name][group][sub_category]['Count'] += 1
                expenses[name][group][sub_category]['Total'] += float(transaction['Amount'])
                total += float(transaction['Amount'])
                count += 1

            expenses[name][group][group] = {'Count': count, 'Total': total}
            table = prettytable.PrettyTable(['Category', 'Sub Category', 'Amount'])

            for sub_category in expenses[name][group].keys():
                if sub_category == group:
                    continue
                else:
                    table.add_row([group, sub_category, "{0:.2f}".format(expenses[name][group][sub_category]['Total'])])

            table.add_row([group, 'All', "{0:.2f}".format(expenses[name][group][group]['Total'])])
            print(table)

    for name in expenses.keys():
        for group in expenses[name].keys():
            if group not in common_expenses.keys():
                common_expenses[group] = dict()
            for sub_category in expenses[name][group].keys():
                if sub_category not in common_expenses[group].keys():
                    common_expenses[group][sub_category] = expenses[name][group][sub_category]
                    common_expenses[group][sub_category][name] = expenses[name][group][sub_category]['Total']
                else:
                    common_expenses[group][sub_category]['Count'] += expenses[name][group][sub_category]['Count']
                    common_expenses[group][sub_category]['Total'] += expenses[name][group][sub_category]['Total']
                    common_expenses[group][sub_category][name] = expenses[name][group][sub_category]['Total']

    print("======== Summary for combined expenses of {0} ========".format(" & ".join(expenses.keys())))

    for group in common_expenses.keys():
        split_expense = dict()
        cols = ['Category', 'Sub Category']
        for name in expenses.keys():
            split_expense[name] = 0.00
            cols.append("{0} Paid".format(name.title()))
        cols.append('Total')
        table = prettytable.PrettyTable(cols)
        for sub_category in common_expenses[group].keys():
            if sub_category == group:
                continue
            else:
                row = [group, sub_category]
                for name in expenses.keys():
                    if name in common_expenses[group][sub_category].keys():
                        split_expense[name] += common_expenses[group][sub_category][name]
                        row.append("{0:.2f}".format(common_expenses[group][sub_category][name]))
                    else:
                        row.append("{0:.2f}".format(0))
                row.append("{0:.2f}".format(common_expenses[group][sub_category]['Total']))
                table.add_row(row)

        row = [group, 'All']
        for name in expenses.keys():
            row.append("{0:.2f}".format(split_expense[name]))
        row.append("{0:.2f}".format(common_expenses[group][group]['Total']))
        table.add_row(row)

        print(table)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:n:s:e:")
    except getopt.GetOptError:
        sys.stderr.write(helper())
        sys.exit(2)

    names_str = None
    path = None
    start_date = None
    end_date = None

    for opt, arg in opts:
        if opt == '-h':
            sys.stdout.write(helper())
            sys.exit()
        elif opt == "-p":
            path = arg
        elif opt == "-n":
            names_str = arg
        elif opt == "-s":
            start_date = time.strptime(arg, "%m/%d/%Y")
        elif opt == "-e":
            end_date = time.strptime(arg, "%m/%d/%Y")

    names = names_str.split(",")
    print("Exporting Financial Information for {0} from {1}".format(names, path))
    transactions = dict()
    categories = set()
    for name in names:
        transactions[name] = read_csv(path + name + ".csv", categories)
        print(categories)

    filtered_transactions, grouped_transactions = filter_transactions(transactions, start_date, end_date)

    summarize(grouped_transactions)


if __name__ == "__main__":
    main(sys.argv[1:])
