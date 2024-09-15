import ast
from personlized_plan.calculate_savings import generate_investment_report
from personlized_plan.ner_mf import extract_entities

def calculate_emi(principal, annual_rate, time_period_years):
    """
    Calculate the Equated Monthly Installment (EMI) for a given principal, annual interest rate, and time period.

    Args:
        principal (float): The loan principal amount.
        annual_rate (float): The annual interest rate in percentage.
        time_period_years (int): The time period of the loan in years.

    Returns:
        tuple: EMI amount, total amount to be paid, and total interest paid.
    """
    monthly_rate = annual_rate / (12 * 100)  # Convert annual rate to monthly rate
    number_of_payments = time_period_years * 12  # Total number of monthly payments

    # EMI calculation formula
    emi = principal * monthly_rate * ((1 + monthly_rate) ** number_of_payments) / (((1 + monthly_rate) ** number_of_payments) - 1)
    total_amount = emi * number_of_payments  # Total amount to be paid over the period
    total_interest = total_amount - principal  # Total interest paid over the period

    return emi, total_amount, total_interest

def calculate_mutual_fund_savings(saving_amount, extended_time_period_years, annual_return_rate):
    """
    Calculate the future value of a mutual fund investment given monthly savings, return rate, and time period.

    Args:
        saving_amount (float): Monthly savings amount.
        extended_time_period_years (int): Investment time period in years.
        annual_return_rate (float): Annual return rate in percentage.

    Returns:
        float: Future value of the investment.
    """
    monthly_savings = saving_amount
    monthly_return_rate = annual_return_rate / (12 * 100)  # Convert annual return rate to monthly rate
    number_of_payments = extended_time_period_years * 12  # Total number of monthly payments

    # Future value calculation formula
    future_value = monthly_savings * (((1 + monthly_return_rate) ** number_of_payments) - 1) / monthly_return_rate
    return future_value

def process_financial_analysis(sentence, saving_amount):
    """
    Process financial analysis based on extracted entities from the sentence and provided savings amount.

    Args:
        sentence (str): The sentence containing details about assets, time period, and total amount.
        saving_amount (float): Monthly savings amount.

    Returns:
        dict: Financial analysis results including EMI details, mutual fund savings, and loan amount.
    """
    # Define interest rates for different asset types
    interest_rates = {
        'car': 8.0,
        'home': 7.0,
        'marriage': 10.0,
        'personal': 12.0
    }

    # Define mutual fund return rate
    mutual_fund_return_rate = 15.0

    try:
        # Extract entities from the sentence
        entities = extract_entities(sentence)
        time_period = entities.get('time_period', [])[0]
        total_amount = entities.get('total_amount', [0])[0]
        assets = entities.get('assets', [])

        # Validate extracted entities
        if not time_period or not total_amount:
            raise ValueError("Time period or total amount is missing in the input sentence.")

        # Determine asset type and corresponding annual interest rate
        asset_type = None
        if 'car' in assets:
            asset_type = 'car'
        elif 'home' in assets:
            asset_type = 'home'
        elif 'marriage' in assets:
            asset_type = 'marriage'
        elif 'personal' in assets:
            asset_type = 'personal'

        annual_interest_rate = interest_rates.get(asset_type, 7.5)  # Default interest rate if asset type is not found

        # Determine EMI period based on the total amount
        if total_amount > 3000000:
            emi_period_years = 10
        elif total_amount > 2000000:
            emi_period_years = 7
        elif total_amount > 1500000:
            emi_period_years = 5
        elif total_amount > 1000000:
            emi_period_years = 3
        elif total_amount > 500000:
            emi_period_years = 2
        else:
            emi_period_years = 1

        # Map EMI period to extended time period
        extended_time_period_years = {
            1: 3,
            2: 5,
            3: 7,
            5: 7,
            7: 9,
            10: 12
        }.get(emi_period_years, emi_period_years)

        # Generate investment report for the given saving amount and time period
        report_str = generate_investment_report(saving_amount, time_period)
        report = ast.literal_eval(report_str)  # Convert report string to dictionary
        future_value_based_on_my_saving = report.get(time_period, [{}])[0].get('future_value', 0)
        loan_amount = total_amount - future_value_based_on_my_saving

        # Calculate EMI details for the given period and extended period
        emi, total_amount_paid, total_interest = calculate_emi(loan_amount, annual_interest_rate, emi_period_years)
        extended_emi, extended_total_amount_paid, extended_total_interest = calculate_emi(loan_amount, annual_interest_rate, extended_time_period_years)

        # Calculate the difference in EMI and the mutual fund savings from that difference
        emi_monthly_difference = emi - extended_emi
        mutual_fund_savings_from_diff = calculate_mutual_fund_savings(emi_monthly_difference, extended_time_period_years, mutual_fund_return_rate)

        # Prepare the result dictionary with detailed analysis
        result = {
            f"Mutual Fund Savings based on your average balance:{saving_amount} after {time_period}": future_value_based_on_my_saving,
            "After savings you Needed Loan Amount of ": loan_amount,
            f"EMI Details for {emi_period_years}": {
                "Standard EMI": {
                    "Years": emi_period_years,
                    "Monthly EMI": emi,
                    f"Total Interest Paid if you will take EMI for {emi_period_years} years": total_interest,
                    f"Total Amount to be Paid if you will take EMI for {emi_period_years} years": total_amount_paid
                },
                f"Extended EMI for {extended_time_period_years}": {
                    "Years": extended_time_period_years,
                    "Monthly EMI": extended_emi,
                    f"Total Interest Paid if you will take EMI for {extended_time_period_years} years": extended_total_interest,
                    f"Total Amount to be Paid if you will take EMI for {extended_time_period_years} years": extended_total_amount_paid
                }
            },
            f"Mutual Fund Savings after {extended_time_period_years} years": mutual_fund_savings_from_diff,
            f"Now if you take plan for {extended_time_period_years} with Mutual Fund Savings then you have to pay only": extended_total_amount_paid-mutual_fund_savings_from_diff,
            f"after choosing EMI plan for {extended_time_period_years} with Mutual Fund Savings you can save up to ":mutual_fund_savings_from_diff
        }

        return result

    except (ValueError, KeyError, IndexError, SyntaxError) as e:
        # Handle errors that occur during processing
        raise Exception(f"Error in processing financial analysis: {e}")
