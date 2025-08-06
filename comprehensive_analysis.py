import os
import glob
import re
from datetime import datetime
from collections import defaultdict
from extraction import extract_transactions_from_pdf

def categorize_transactions(transactions):
    """
    Categorize transactions into the specific types requested:
    1. Deposits
    2. Paper Deposits  
    3. Transfers from other accounts
    4. Checks
    5. ATM/Debit Card transactions
    6. Electronic Withdrawals
    7. Fees and Services
    """
    
    categories = {
        'deposits': [],
        'paper_deposits': [],
        'transfers': [],
        'checks': [],
        'atm_debit': [],
        'electronic_withdrawals': [],
        'fees_services': []
    }
    
    for txn in transactions:
        description = txn['description'].lower()
        amount = txn['amount']
        txn_type = txn.get('type', '').lower()
        
        # Use the type field from the parser if available, otherwise categorize by description
        if txn_type:
            if txn_type == 'deposit':
                categories['paper_deposits'].append(txn)
            elif txn_type == 'transfer':
                categories['transfers'].append(txn)
            elif txn_type == 'wire_transfer':
                categories['electronic_withdrawals'].append(txn)
            elif txn_type == 'zelle':
                categories['electronic_withdrawals'].append(txn)
            elif txn_type in ['overdraft_fee', 'returned_item_fee', 'service_charge', 'other_fee']:
                categories['fees_services'].append(txn)
            elif txn_type in ['wells_fargo_payment', 'toyota_payment', 'ally_payment', 'gm_financial_payment', 'ford_payment', 'td_auto_payment', 'bridgecrest_payment']:
                categories['electronic_withdrawals'].append(txn)
            else:
                # Fallback categorization
                if amount > 0:
                    categories['deposits'].append(txn)
                elif amount < 0:
                    categories['electronic_withdrawals'].append(txn)
        else:
            # Fallback categorization based on description
            if 'paper deposit' in description:
                categories['paper_deposits'].append(txn)
            elif 'transfer' in description or 'webfundstransfer' in description:
                categories['transfers'].append(txn)
            elif 'check' in description:
                categories['checks'].append(txn)
            elif any(keyword in description for keyword in ['atm', 'debit', 'pos', 'purchase']):
                categories['atm_debit'].append(txn)
            elif any(keyword in description for keyword in ['fee', 'service charge', 'overdraft']):
                categories['fees_services'].append(txn)
            elif amount > 0:
                categories['deposits'].append(txn)
            elif amount < 0:
                categories['electronic_withdrawals'].append(txn)
    
    return categories

def group_similar_transactions(transactions):
    """Group similar transactions and calculate totals"""
    groups = defaultdict(list)
    
    for txn in transactions:
        # Create a key for grouping based on description
        description = txn['description']
        txn_type = txn.get('type', '').lower()
        
        # Extract merchant/service name based on transaction type
        if txn_type == 'deposit':
            merchant = "Paper Deposits"
        elif txn_type == 'transfer':
            merchant = "WebFunds Transfer"
        elif txn_type == 'wire_transfer':
            merchant = "Wire Transfer"
        elif txn_type == 'zelle':
            merchant = "Zelle"
        elif txn_type in ['overdraft_fee', 'returned_item_fee', 'service_charge', 'other_fee']:
            merchant = "Fees"
        elif txn_type in ['wells_fargo_payment', 'toyota_payment', 'ally_payment', 'gm_financial_payment', 'ford_payment', 'td_auto_payment', 'bridgecrest_payment']:
            # Extract the specific payment type
            if 'wells_fargo' in txn_type:
                merchant = "Wells Fargo Payment"
            elif 'toyota' in txn_type:
                merchant = "Toyota Payment"
            elif 'ally' in txn_type:
                merchant = "Ally Payment"
            elif 'gm_financial' in txn_type:
                merchant = "GM Financial Payment"
            elif 'ford' in txn_type:
                merchant = "Ford Payment"
            elif 'td_auto' in txn_type:
                merchant = "TD Auto Payment"
            elif 'bridgecrest' in txn_type:
                merchant = "Bridgecrest Payment"
            else:
                merchant = "Other Payment"
        else:
            # General categorization based on description
            if '*' in description:
                # For card transactions like "WALMART *1234"
                merchant = description.split('*')[0].strip()
            elif 'check #' in description.lower():
                merchant = "Checks"
            elif 'paper deposit' in description.lower():
                merchant = "Paper Deposits"
            elif 'transfer' in description.lower():
                merchant = "Transfers"
            elif 'fee' in description.lower():
                merchant = "Fees"
            elif 'zelle' in description.lower():
                merchant = "Zelle"
            elif 'wire' in description.lower():
                merchant = "Wire Transfer"
            else:
                # Take first meaningful word
                words = description.split()
                if len(words) > 0:
                    merchant = words[0]
                else:
                    merchant = description
        
        groups[merchant].append(txn)
    
    # Calculate totals for each group
    group_totals = {}
    for merchant, txns in groups.items():
        total_amount = sum(txn['amount'] for txn in txns)
        group_totals[merchant] = {
            'total_amount': total_amount,
            'transaction_count': len(txns),
            'transactions': txns
        }
    
    return group_totals

def print_category_summary(category_name, transactions, grouped_totals):
    """Print summary for a specific category"""
    if not transactions:
        print(f"\n{category_name.upper().replace('_', ' ')}: No transactions found")
        return
    
    print(f"\n{'='*80}")
    print(f"{category_name.upper().replace('_', ' ')}")
    print(f"{'='*80}")
    
    # Overall summary
    total_amount = sum(txn['amount'] for txn in transactions)
    print(f"Total Transactions: {len(transactions)}")
    print(f"Total Amount: ${total_amount:.2f}")
    
    # Grouped summary
    if grouped_totals:
        print(f"\nGrouped Transactions:")
        print(f"{'Merchant/Service':<30} {'Count':<8} {'Total Amount':<15} {'Avg Amount'}")
        print(f"{'-'*30} {'-'*8} {'-'*15} {'-'*10}")
        
        # Sort by total amount (absolute value, descending)
        sorted_groups = sorted(grouped_totals.items(), 
                             key=lambda x: abs(x[1]['total_amount']), 
                             reverse=True)
        
        for merchant, data in sorted_groups:
            count = data['transaction_count']
            total = data['total_amount']
            avg = total / count if count > 0 else 0
            
            print(f"{merchant[:29]:<30} {count:<8} ${total:<14.2f} ${avg:.2f}")
    
    print(f"{'='*80}")

def analyze_statement(pdf_path):
    """Analyze a single statement file"""
    print(f"\nAnalyzing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    # Extract transactions
    transactions = extract_transactions_from_pdf(pdf_path)
    
    if not transactions:
        print("No transactions found in this statement.")
        return
    
    # Categorize transactions
    categories = categorize_transactions(transactions)
    
    # Group and analyze each category
    for category_name, category_transactions in categories.items():
        if category_transactions:
            grouped_totals = group_similar_transactions(category_transactions)
            print_category_summary(category_name, category_transactions, grouped_totals)
        else:
            print(f"\n{category_name.upper().replace('_', ' ')}: No transactions found")

def main():
    """Main function to analyze statements"""
    # Look for PDF files in the statements directory
    statements_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "statements")
    pdf_files = glob.glob(os.path.join(statements_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {statements_dir} directory.")
        print("Please place your bank statement PDF files in the statements/ directory.")
        return
    
    # Sort files by modification time (newest first)
    pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    print(f"Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        size = os.path.getsize(pdf_file) / 1024
        print(f"{i}. {os.path.basename(pdf_file)} ({size:.1f}KB)")
    
    # Let user choose which file to analyze
    if len(pdf_files) > 1:
        while True:
            try:
                choice = input(f"\nSelect a file to analyze (1-{len(pdf_files)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(pdf_files):
                    selected_file = pdf_files[choice_num - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(pdf_files)}")
            except ValueError:
                print("Please enter a valid number")
    else:
        selected_file = pdf_files[0]
    
    # Analyze the selected statement
    analyze_statement(selected_file)

if __name__ == "__main__":
    main()
