import json
import matplotlib.pyplot as plt
from datetime import datetime
import calendar
import os
from collections import defaultdict
import csv

# Initialize variables
transactions = {
    'income': [],
    'expenses': [],
    'savings_goals': [],
    'investments': []
}

# Load transactions data from file
def load_data():
    global transactions
    try:
        with open('finance_data.json', 'r') as file:
            transactions = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Initialize with empty data if file doesn't exist or is corrupted
        transactions = {
            'income': [],
            'expenses': [],
            'savings_goals': [],
            'investments': []
        }

# Save transactions data to file
def save_data():
    with open('finance_data.json', 'w') as file:
        json.dump(transactions, file, indent=4)

# Backup data to CSV
def backup_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    for data_type in transactions:
        filename = f"{backup_dir}/{data_type}_{timestamp}.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if transactions[data_type]:
                writer.writerow(transactions[data_type][0].keys())
                for item in transactions[data_type]:
                    writer.writerow(item.values())

# Add a transaction for income
def add_income():
    try:
        amount = float(input('Enter income amount: '))
        source = input('Enter income source (e.g., Salary, Freelance): ')
        date = input('Enter date (YYYY-MM-DD) or leave blank for today: ')
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        income = {
            'amount': amount,
            'source': source,
            'date': date,
            'timestamp': datetime.now().isoformat()
        }
        transactions['income'].append(income)
        print(f'Income of {amount} from {source} added successfully!')
    except ValueError:
        print('Invalid amount! Please enter a valid number.')

# Add a transaction for expense
def add_expense():
    description = input('Enter expense description: ')
    try:
        amount = float(input('Enter expense amount: '))
        category = input('Enter expense category (e.g., Food, Transport): ')
        payment_method = input('Enter payment method (Cash/Card/Digital Wallet): ')
        date = input('Enter date (YYYY-MM-DD) or leave blank for today: ')
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        expense = {
            'description': description,
            'amount': amount,
            'category': category,
            'payment_method': payment_method,
            'date': date,
            'timestamp': datetime.now().isoformat()
        }
        transactions['expenses'].append(expense)
        print('Expense added successfully!')
    except ValueError:
        print('Invalid amount! Please enter a valid number.')

# Calculate and display current savings
def calculate_savings():
    total_income = sum(item['amount'] for item in transactions['income'])
    total_expenses = sum(item['amount'] for item in transactions['expenses'])
    savings = total_income - total_expenses
    print(f'\n=== Financial Summary ===')
    print(f'Total Income: {total_income:.2f}')
    print(f'Total Expenses: {total_expenses:.2f}')
    print(f'Current Savings: {savings:.2f}')
    
    # Check savings goals
    for goal in transactions['savings_goals']:
        progress = min(savings / goal['target_amount'] * 100, 100)
        print(f"\nGoal: {goal['name']}")
        print(f"Target: {goal['target_amount']:.2f} by {goal['target_date']}")
        print(f"Progress: {progress:.1f}%")
    
    return savings

# Generate expense report by category with time filters
def generate_expense_report_category():
    print("\n=== Expense Report Options ===")
    print("1. View by category")
    print("2. View by time period")
    print("3. View by payment method")
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        categories = set(expense['category'] for expense in transactions['expenses'])
        print('\nAvailable categories:', ', '.join(categories))
        category = input('Enter category: ')
        
        category_expenses = [e for e in transactions['expenses'] if e['category'] == category]
        if not category_expenses:
            print(f'No expenses found for category: {category}')
            return
            
        total = sum(e['amount'] for e in category_expenses)
        print(f'\n=== {category} Expenses ===')
        print(f'Total spent: {total:.2f}')
        print(f'Number of transactions: {len(category_expenses)}')
        print('\nRecent transactions:')
        for expense in sorted(category_expenses, key=lambda x: x['date'], reverse=True)[:5]:
            print(f"{expense['date']}: {expense['description']} - {expense['amount']:.2f}")
    
    elif choice == '2':
        print("\n=== Time Period Options ===")
        print("1. This month")
        print("2. Last month")
        print("3. This year")
        print("4. Custom date range")
        period = input("Enter your choice (1-4): ")
        
        now = datetime.now()
        if period == '1':
            # This month
            start_date = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        elif period == '2':
            # Last month
            if now.month == 1:
                start_date = datetime(now.year-1, 12, 1).strftime("%Y-%m-%d")
                end_date = datetime(now.year-1, 12, 31).strftime("%Y-%m-%d")
            else:
                last_day = calendar.monthrange(now.year, now.month-1)[1]
                start_date = datetime(now.year, now.month-1, 1).strftime("%Y-%m-%d")
                end_date = datetime(now.year, now.month-1, last_day).strftime("%Y-%m-%d")
        elif period == '3':
            # This year
            start_date = datetime(now.year, 1, 1).strftime("%Y-%m-%d")
            end_date = now.strftime("%Y-%m-%d")
        elif period == '4':
            # Custom range
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
        else:
            print("Invalid choice")
            return
            
        period_expenses = [e for e in transactions['expenses'] if start_date <= e['date'] <= end_date]
        if not period_expenses:
            print(f'No expenses found between {start_date} and {end_date}')
            return
            
        total = sum(e['amount'] for e in period_expenses)
        print(f'\n=== Expenses from {start_date} to {end_date} ===')
        print(f'Total spent: {total:.2f}')
        
        # Breakdown by category
        category_totals = defaultdict(float)
        for expense in period_expenses:
            category_totals[expense['category']] += expense['amount']
        
        print("\nBy Category:")
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"{category}: {amount:.2f} ({amount/total*100:.1f}%)")
    
    elif choice == '3':
        methods = set(expense['payment_method'] for expense in transactions['expenses'])
        print('\nAvailable payment methods:', ', '.join(methods))
        method = input('Enter payment method: ')
        
        method_expenses = [e for e in transactions['expenses'] if e['payment_method'] == method]
        if not method_expenses:
            print(f'No expenses found for payment method: {method}')
            return
            
        total = sum(e['amount'] for e in method_expenses)
        print(f'\n=== {method} Expenses ===')
        print(f'Total spent: {total:.2f}')
        
        # Breakdown by category
        category_totals = defaultdict(float)
        for expense in method_expenses:
            category_totals[expense['category']] += expense['amount']
        
        print("\nBy Category:")
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"{category}: {amount:.2f}")

# Generate visualizations
def generate_visualizations():
    print("\n=== Visualization Options ===")
    print("1. Expense by Category (Pie Chart)")
    print("2. Monthly Spending Trend (Line Chart)")
    print("3. Income vs Expenses (Bar Chart)")
    print("4. Payment Method Distribution (Donut Chart)")
    choice = input("Enter your choice (1-4): ")
    
    if choice == '1':
        # Expense by Category Pie Chart
        category_totals = defaultdict(float)
        for expense in transactions['expenses']:
            category_totals[expense['category']] += expense['amount']
        
        if not category_totals:
            print("No expense data available")
            return
            
        labels = list(category_totals.keys())
        values = list(category_totals.values())
        
        plt.figure(figsize=(10, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Expenses by Category')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
    
    elif choice == '2':
        # Monthly Spending Trend Line Chart
        monthly_totals = defaultdict(float)
        for expense in transactions['expenses']:
            date = datetime.strptime(expense['date'], "%Y-%m-%d")
            month_year = f"{date.year}-{date.month:02d}"
            monthly_totals[month_year] += expense['amount']
        
        if not monthly_totals:
            print("No expense data available")
            return
            
        months = sorted(monthly_totals.keys())
        amounts = [monthly_totals[m] for m in months]
        
        plt.figure(figsize=(10, 6))
        plt.plot(months, amounts, marker='o')
        plt.title('Monthly Spending Trend')
        plt.xlabel('Month')
        plt.ylabel('Amount Spent')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    elif choice == '3':
        # Income vs Expenses Bar Chart
        monthly_income = defaultdict(float)
        monthly_expenses = defaultdict(float)
        
        for income in transactions['income']:
            date = datetime.strptime(income['date'], "%Y-%m-%d")
            month_year = f"{date.year}-{date.month:02d}"
            monthly_income[month_year] += income['amount']
        
        for expense in transactions['expenses']:
            date = datetime.strptime(expense['date'], "%Y-%m-%d")
            month_year = f"{date.year}-{date.month:02d}"
            monthly_expenses[month_year] += expense['amount']
        
        all_months = sorted(set(monthly_income.keys()).union(set(monthly_expenses.keys())))
        income_data = [monthly_income.get(m, 0) for m in all_months]
        expense_data = [monthly_expenses.get(m, 0) for m in all_months]
        
        plt.figure(figsize=(12, 6))
        bar_width = 0.35
        index = range(len(all_months))
        
        plt.bar(index, income_data, bar_width, label='Income')
        plt.bar([i + bar_width for i in index], expense_data, bar_width, label='Expenses')
        
        plt.title('Monthly Income vs Expenses')
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.xticks([i + bar_width/2 for i in index], all_months, rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    elif choice == '4':
        # Payment Method Donut Chart
        method_totals = defaultdict(float)
        for expense in transactions['expenses']:
            method_totals[expense['payment_method']] += expense['amount']
        
        if not method_totals:
            print("No expense data available")
            return
            
        labels = list(method_totals.keys())
        values = list(method_totals.values())
        
        plt.figure(figsize=(8, 8))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.4))
        plt.title('Payment Method Distribution')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

# Add a savings goal
def add_savings_goal():
    name = input('Enter goal name (e.g., Vacation, Emergency Fund): ')
    try:
        target_amount = float(input('Enter target amount: '))
        target_date = input('Enter target date (YYYY-MM-DD): ')
        
        goal = {
            'name': name,
            'target_amount': target_amount,
            'target_date': target_date,
            'created_at': datetime.now().isoformat()
        }
        transactions['savings_goals'].append(goal)
        print(f'Savings goal "{name}" added successfully!')
    except ValueError:
        print('Invalid amount! Please enter a valid number.')

# Add investment tracking
def add_investment():
    name = input('Enter investment name (e.g., Stock, Mutual Fund): ')
    try:
        amount = float(input('Enter invested amount: '))
        investment_type = input('Enter investment type: ')
        date = input('Enter date (YYYY-MM-DD) or leave blank for today: ')
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        investment = {
            'name': name,
            'amount': amount,
            'type': investment_type,
            'date': date,
            'timestamp': datetime.now().isoformat()
        }
        transactions['investments'].append(investment)
        print(f'Investment in {name} added successfully!')
    except ValueError:
        print('Invalid amount! Please enter a valid number.')

# View investments
def view_investments():
    if not transactions['investments']:
        print("No investments recorded yet.")
        return
    
    total_invested = sum(i['amount'] for i in transactions['investments'])
    print(f"\n=== Investment Portfolio ===")
    print(f"Total Invested: {total_invested:.2f}")
    
    print("\nBy Investment Type:")
    type_totals = defaultdict(float)
    for investment in transactions['investments']:
        type_totals[investment['type']] += investment['amount']
    
    for inv_type, amount in type_totals.items():
        print(f"{inv_type}: {amount:.2f} ({amount/total_invested*100:.1f}%)")
    
    print("\nRecent Investments:")
    for investment in sorted(transactions['investments'], key=lambda x: x['date'], reverse=True)[:5]:
        print(f"{investment['date']}: {investment['name']} ({investment['type']}) - {investment['amount']:.2f}")

# Budget planning feature
def budget_planning():
    print("\n=== Budget Planning ===")
    print("1. Set monthly budget")
    print("2. View budget vs actual")
    choice = input("Enter your choice (1-2): ")
    
    if choice == '1':
        category = input("Enter budget category: ")
        try:
            amount = float(input("Enter budget amount: "))
            month_year = input("Enter month and year (MM-YYYY) or leave blank for current month: ")
            if not month_year:
                now = datetime.now()
                month_year = f"{now.month:02d}-{now.year}"
            
            # Check if budget already exists for this category and month
            for budget in transactions.get('budgets', []):
                if budget['category'] == category and budget['month_year'] == month_year:
                    budget['amount'] = amount
                    print(f"Updated budget for {category} in {month_year}")
                    return
            
            # Add new budget
            budget = {
                'category': category,
                'amount': amount,
                'month_year': month_year,
                'created_at': datetime.now().isoformat()
            }
            if 'budgets' not in transactions:
                transactions['budgets'] = []
            transactions['budgets'].append(budget)
            print(f"Budget set for {category} in {month_year}")
        
        except ValueError:
            print("Invalid amount! Please enter a valid number.")
    
    elif choice == '2':
        month_year = input("Enter month and year (MM-YYYY) or leave blank for current month: ")
        if not month_year:
            now = datetime.now()
            month_year = f"{now.month:02d}-{now.year}"
        
        # Get budgets for the selected month
        month_budgets = [b for b in transactions.get('budgets', []) if b['month_year'] == month_year]
        if not month_budgets:
            print(f"No budgets set for {month_year}")
            return
        
        # Get expenses for the selected month
        month, year = map(int, month_year.split('-'))
        start_date = datetime(year, month, 1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).strftime("%Y-%m-%d")
        
        month_expenses = [e for e in transactions['expenses'] if start_date <= e['date'] <= end_date]
        
        print(f"\n=== Budget vs Actual for {month_year} ===")
        for budget in month_budgets:
            category = budget['category']
            budget_amount = budget['amount']
            actual_amount = sum(e['amount'] for e in month_expenses if e['category'] == category)
            remaining = budget_amount - actual_amount
            percentage = (actual_amount / budget_amount * 100) if budget_amount > 0 else 0
            
            status = "Under" if remaining >= 0 else "Over"
            print(f"\n{category}:")
            print(f"  Budget: {budget_amount:.2f}")
            print(f"  Actual: {actual_amount:.2f} ({percentage:.1f}%)")
            print(f"  {status} budget by: {abs(remaining):.2f}")

# Main menu
def main():
    load_data()
    
    while True:
        print('\n' + '='*50)
        print('========== BucksBot (Automated money manager) ==========')
        print('1. Add Income')
        print('2. Add Expense')
        print('3. Financial Summary & Savings')
        print('4. Expense Reports')
        print('5. Visualizations')
        print('6. Savings Goals')
        print('7. Investment Tracking')
        print('8. Budget Planning')
        print('9. Backup Data')
        print('10. Exit')
        print('='*50)

        try:
            choice = input('Enter your choice (1-10): ')
            
            if choice == '1':
                add_income()
            elif choice == '2':
                add_expense()
            elif choice == '3':
                calculate_savings()
            elif choice == '4':
                generate_expense_report_category()
            elif choice == '5':
                generate_visualizations()
            elif choice == '6':
                print("\n=== Savings Goals ===")
                print("1. Add Savings Goal")
                print("2. View Goals Progress")
                sub_choice = input("Enter your choice (1-2): ")
                if sub_choice == '1':
                    add_savings_goal()
                elif sub_choice == '2':
                    calculate_savings()  # This already shows goal progress
            elif choice == '7':
                print("\n=== Investment Tracking ===")
                print("1. Add Investment")
                print("2. View Investments")
                sub_choice = input("Enter your choice (1-2): ")
                if sub_choice == '1':
                    add_investment()
                elif sub_choice == '2':
                    view_investments()
            elif choice == '8':
                budget_planning()
            elif choice == '9':
                backup_data()
                print("Data backed up successfully!")
            elif choice == '10':
                save_data()
                print("Thank you for using the Finance Tracker!")
                break
            else:
                print('Invalid choice! Please enter a number between 1-10.')
            
            # Auto-save after each operation
            save_data()
            
        except ValueError:
            print('Invalid input! Please enter a valid number.')

if __name__ == '__main__':
    main()
