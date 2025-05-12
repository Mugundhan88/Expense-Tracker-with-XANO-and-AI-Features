#!/usr/bin/env python3.11
import json
from collections import defaultdict
from datetime import datetime
import argparse

def load_expenses(file_path):
    """Loads expense data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            expenses_data = json.load(f)
        # Ensure data is a list of expense objects
        if not isinstance(expenses_data, list):
            print("Error: Expense data should be a list of objects.")
            return None
        for expense in expenses_data:
            if not all(k in expense for k in ["category_name", "amount", "expense_date"]):
                print(f"Error: Expense object missing required keys (category_name, amount, expense_date): {expense}")
                return None
            # Convert amount to float and date to datetime object
            try:
                expense["amount"] = float(expense["amount"])
                expense["expense_date"] = datetime.strptime(expense["expense_date"], "%Y-%m-%d")
            except ValueError as e:
                print(f"Error converting data types for expense {expense}: {e}")
                return None
        return expenses_data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading expenses: {e}")
        return None

def analyze_spending_patterns(expenses, period="monthly", start_date_str=None, end_date_str=None):
    """Analyzes spending patterns from a list of expense objects."""
    if not expenses:
        return {
            "summary": {"total_spent": 0, "number_of_transactions": 0},
            "by_category": [],
            "over_time": []
        }

    # Filter by date range if provided
    filtered_expenses = []
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

    for expense in expenses:
        if start_date and expense["expense_date"] < start_date:
            continue
        if end_date and expense["expense_date"] > end_date:
            continue
        filtered_expenses.append(expense)
    
    if not filtered_expenses:
         return {
            "summary": {"total_spent": 0, "number_of_transactions": 0, "period_info": f"No expenses found for the period {start_date_str} to {end_date_str}"},
            "by_category": [],
            "over_time": []
        }

    total_spent = sum(e["amount"] for e in filtered_expenses)
    num_transactions = len(filtered_expenses)

    # Analysis by category
    by_category = defaultdict(float)
    for expense in filtered_expenses:
        by_category[expense["category_name"]] += expense["amount"]
    
    analysis_by_category = []
    for category, total in by_category.items():
        analysis_by_category.append({
            "category_name": category,
            "total": round(total, 2),
            "percentage": round((total / total_spent) * 100, 2) if total_spent else 0
        })
    analysis_by_category.sort(key=lambda x: x["total"], reverse=True)

    # Analysis over time (e.g., monthly)
    over_time = defaultdict(float)
    if period == "monthly":
        for expense in filtered_expenses:
            month_year = expense["expense_date"].strftime("%Y-%m") # e.g., "2023-04"
            over_time[month_year] += expense["amount"]
    elif period == "yearly":
         for expense in filtered_expenses:
            year = expense["expense_date"].strftime("%Y")
            over_time[year] += expense["amount"]
    # Add more periods like 'weekly' if needed
    
    analysis_over_time = []
    for p_label, total in sorted(over_time.items()):
        analysis_over_time.append({
            "period_label": p_label,
            "total": round(total, 2)
        })

    return {
        "summary": {
            "total_spent": round(total_spent, 2),
            "number_of_transactions": num_transactions,
            "start_date_applied": start_date_str if start_date else "N/A",
            "end_date_applied": end_date_str if end_date else "N/A",
            "analysis_period_grouping": period
        },
        "by_category": analysis_by_category,
        "over_time": analysis_over_time
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze spending patterns from expense data.")
    parser.add_argument("expenses_file_path", help="Path to the JSON file containing expense data.")
    parser.add_argument("--output_json", help="Path to save the analysis data as JSON.", default=None)
    parser.add_argument("--period", help="Time period for aggregation (e.g., 'monthly', 'yearly').", default="monthly", choices=["monthly", "yearly"])
    parser.add_argument("--start_date", help="Start date for analysis (YYYY-MM-DD).", default=None)
    parser.add_argument("--end_date", help="End date for analysis (YYYY-MM-DD).", default=None)

    args = parser.parse_args()

    print(f"Loading expenses from: {args.expenses_file_path}")
    expenses_list = load_expenses(args.expenses_file_path)

    if expenses_list:
        print("Analyzing spending patterns...")
        analysis_result = analyze_spending_patterns(expenses_list, args.period, args.start_date, args.end_date)
        
        print("--- Spending Analysis Result ---")
        print(json.dumps(analysis_result, indent=2))
        print("--------------------------------")

        if args.output_json:
            try:
                with open(args.output_json, "w") as f:
                    json.dump(analysis_result, f, indent=2)
                print(f"Saved analysis data to {args.output_json}")
            except Exception as e:
                print(f"Error saving JSON output: {e}")
    else:
        print("Could not load or process expense data.")

    # Example usage from command line:
    # Create a sample_expenses.json file with content like:
    # [
    #   {"category_name": "Food", "amount": 12.50, "expense_date": "2023-04-10"},
    #   {"category_name": "Transport", "amount": 30.00, "expense_date": "2023-04-12"},
    #   {"category_name": "Food", "amount": 25.00, "expense_date": "2023-04-15"},
    #   {"category_name": "Utilities", "amount": 75.00, "expense_date": "2023-05-01"},
    #   {"category_name": "Food", "amount": 10.00, "expense_date": "2023-05-05"}
    # ]
    # Then run: python3.11 spending_analyzer.py sample_expenses.json --output_json analysis_output.json --period monthly --start_date 2023-04-01 --end_date 2023-04-30

