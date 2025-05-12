#!/usr/bin/env python3.11
import json
from collections import defaultdict
from datetime import datetime, timedelta
import argparse
import statistics # For mean and potentially stdev if needed for more advanced predictions

def load_expenses_for_prediction(file_path):
    """Loads and preprocesses expense data from a JSON file for prediction."""
    try:
        with open(file_path, 'r') as f:
            expenses_data = json.load(f)
        if not isinstance(expenses_data, list):
            print("Error: Expense data should be a list of objects.")
            return None
        
        processed_expenses = []
        for expense in expenses_data:
            if not all(k in expense for k in ["category_name", "amount", "expense_date"]):
                print(f"Error: Expense object missing required keys: {expense}")
                return None
            try:
                expense["amount"] = float(expense["amount"])
                # Ensure date is parsed correctly, assuming YYYY-MM-DD format
                expense["expense_date"] = datetime.strptime(expense["expense_date"].split('T')[0], "%Y-%m-%d")
                processed_expenses.append(expense)
            except ValueError as e:
                print(f"Error converting data types for expense {expense}: {e}")
                return None
        return processed_expenses
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def predict_future_spending(expenses, category_name=None, future_periods=3, period_type="monthly"):
    """Predicts future spending based on historical averages."""
    if not expenses:
        return {"error": "No expense data provided for prediction."}

    # Filter by category if specified
    if category_name:
        expenses = [e for e in expenses if e["category_name"].lower() == category_name.lower()]
        if not expenses:
            return {"error": f"No expenses found for category: {category_name}"}

    # Aggregate spending by period (e.g., monthly)
    period_spending = defaultdict(float)
    if period_type == "monthly":
        for expense in expenses:
            month_year = expense["expense_date"].strftime("%Y-%m")
            period_spending[month_year] += expense["amount"]
    else:
        return {"error": "Currently, only 'monthly' prediction period is supported."}

    if not period_spending:
        return {"error": "Not enough historical data for the selected category/period to make predictions."}

    # Calculate average spending per period
    historical_amounts = list(period_spending.values())
    if not historical_amounts:
        return {"error": "No historical amounts to calculate average from."}
        
    average_spend_per_period = statistics.mean(historical_amounts)
    
    # Determine the last historical period to start predictions from
    last_historical_period_str = max(period_spending.keys())
    last_historical_date = datetime.strptime(last_historical_period_str + "-01", "%Y-%m-%d") # Use 1st of month

    predictions = []
    current_prediction_date = last_historical_date
    for _ in range(future_periods):
        if period_type == "monthly":
            # Move to the next month
            # Handle month overflow correctly
            if current_prediction_date.month == 12:
                current_prediction_date = current_prediction_date.replace(year=current_prediction_date.year + 1, month=1)
            else:
                current_prediction_date = current_prediction_date.replace(month=current_prediction_date.month + 1)
            
            period_label = current_prediction_date.strftime("%Y-%m")
        
        predictions.append({
            "period_label": period_label,
            "predicted_spend": round(average_spend_per_period, 2),
            "confidence_level": "medium" # Simple placeholder
        })

    return {
        "category_name": category_name if category_name else "All Categories",
        "average_historical_spend_per_period": round(average_spend_per_period, 2),
        "historical_periods_analyzed": len(historical_amounts),
        "predictions": predictions
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict future spending based on historical expense data.")
    parser.add_argument("expenses_file_path", help="Path to the JSON file containing expense data.")
    parser.add_argument("--output_json", help="Path to save the prediction data as JSON.", default=None)
    parser.add_argument("--category", help="Specific category to predict for (optional).", default=None)
    parser.add_argument("--future_periods", help="Number of future periods to predict.", type=int, default=3)
    parser.add_argument("--period_type", help="Type of period for prediction (e.g., 'monthly').", default="monthly", choices=["monthly"])

    args = parser.parse_args()

    print(f"Loading expenses from: {args.expenses_file_path}")
    expenses_list = load_expenses_for_prediction(args.expenses_file_path)

    if expenses_list:
        print(f"Predicting future spending for category '{args.category if args.category else 'All Categories'}'...")
        prediction_result = predict_future_spending(expenses_list, args.category, args.future_periods, args.period_type)
        
        print("--- Predictive Budgeting Result ---")
        print(json.dumps(prediction_result, indent=2))
        print("-----------------------------------")

        if args.output_json:
            try:
                with open(args.output_json, "w") as f:
                    json.dump(prediction_result, f, indent=2)
                print(f"Saved prediction data to {args.output_json}")
            except Exception as e:
                print(f"Error saving JSON output: {e}")
    else:
        print("Could not load or process expense data for prediction.")

    # Example usage from command line:
    # Using the same sample_expenses.json as spending_analyzer.py
    # python3.11 predictive_budgeter.py sample_expenses.json --output_json prediction_output.json --category Food --future_periods 3

