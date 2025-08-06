import os
import glob
import pdfplumber
from datetime import datetime
from parsers import AVAILABLE_PARSERS

def extract_transactions_from_pdf(pdf_path):
    """Extract raw transaction data from PDF statement"""
    print("\nAnalyzing statement format...")
    
    # Extract first 1000 characters for format detection
    with pdfplumber.open(pdf_path) as pdf:
        # Extract all text from the PDF
        all_text = ""
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            all_text += page_text + "\n"
        
        print("\nFull statement text:")
        print("-" * 50)
        print(all_text)
        print("-" * 50)
    
    for parser_class in AVAILABLE_PARSERS:
        print(f"\nTrying {parser_class.__name__}...")
        parser = parser_class(pdf_path)
        if parser.detect_format():
            print(f"Success! Detected format: {parser_class.__name__}")
            transactions = parser.extract_transactions()
            if transactions:
                print(f"Found {len(transactions)} transactions")
                return transactions
            else:
                print("No transactions found in the statement")
        else:
            print(f"{parser_class.__name__} did not match")
    
    print("\nUnknown bank statement format. Please implement a new parser for this format.")
    return []

def print_transactions(transactions):
    """Print transactions in a clean format"""
    if not transactions:
        print("No transactions found.")
        return
    
    print(f"\nFound {len(transactions)} transactions:")
    print("-" * 80)
    print(f"{'Date':<12} {'Amount':<12} {'Description'}")
    print("-" * 80)
    
    for txn in transactions:
        amount_str = f"${txn['amount']:.2f}"
        print(f"{txn['date']:<12} {amount_str:<12} {txn['description']}")

def save_transactions_to_csv(transactions, filename="transactions.csv"):
    """Save transactions to CSV file"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'amount', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for txn in transactions:
            writer.writerow({
                'date': txn['date'],
                'amount': txn['amount'],
                'description': txn['description']
            })
    
    print(f"\nTransactions saved to {filename}")

def group_transactions_by_merchant(transactions):
    """Group transactions by merchant and sum amounts"""
    from collections import defaultdict
    
    merchant_groups = defaultdict(list)
    
    for txn in transactions:
        # Extract merchant name (first word or first few words)
        description = txn['description']
        
        # Try to identify merchant patterns
        if '*' in description:
            # For services like "Lyft *1Ride12-29" 
            merchant = description.split('*')[0].strip()
        elif description.startswith('Check #'):
            merchant = "Checks"
        else:
            # General case: take first word or meaningful part
            words = description.split()
            if len(words) > 0:
                merchant = words[0]
            else:
                merchant = description
        
        merchant_groups[merchant].append(txn)
    
    # Calculate totals for each merchant
    merchant_totals = {}
    for merchant, txns in merchant_groups.items():
        total_amount = sum(txn['amount'] for txn in txns)
        merchant_totals[merchant] = {
            'total_amount': total_amount,
            'transaction_count': len(txns),
            'transactions': txns
        }
    
    return merchant_totals

def print_grouped_transactions(merchant_totals, show_details=False):
    """Print grouped transactions with totals"""
    if not merchant_totals:
        print("No transactions to group.")
        return
    
    print(f"\nGrouped Transactions Summary:")
    print("-" * 80)
    print(f"{'Merchant':<25} {'Count':<8} {'Total Amount':<15} {'Avg Amount'}")
    print("-" * 80)
    
    # Sort by total amount (absolute value, descending)
    sorted_merchants = sorted(merchant_totals.items(), 
                            key=lambda x: abs(x[1]['total_amount']), 
                            reverse=True)
    
    grand_total = 0
    total_transactions = 0
    
    for merchant, data in sorted_merchants:
        count = data['transaction_count']
        total = data['total_amount']
        avg = total / count if count > 0 else 0
        
        print(f"{merchant[:24]:<25} {count:<8} ${total:<14.2f} ${avg:.2f}")
        
        grand_total += total
        total_transactions += count
        
        if show_details:
            print(f"  Details:")
            for txn in data['transactions']:
                print(f"    {txn['date']} ${txn['amount']:>8.2f} {txn['description'][:50]}")
            print()
    
    print("-" * 80)
    print(f"{'TOTAL':<25} {total_transactions:<8} ${grand_total:<14.2f}")
    print("-" * 80)

# Main execution
if __name__ == "__main__":
    # Look for PDF files in the statements directory
    statements_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "statements")  # Absolute path to statements directory
    pdf_files = glob.glob(os.path.join(statements_dir, "*.pdf"))
    
    # Sort files by modification time (newest first)
    pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    if not pdf_files:
        print(f"No PDF files found in {statements_dir} directory.")
        print("Please place your bank statement PDF files in the statements/ directory.")
        exit()
    
    print(f"\nFound {len(pdf_files)} PDF files in {statements_dir}:")
    for i, pdf_file in enumerate(pdf_files, 1):
        size = os.path.getsize(pdf_file) / 1024  # Convert to KB
        print(f"{i}. {os.path.basename(pdf_file)} ({size:.1f}KB)")
    
    # If multiple PDF files found, let user choose
    if len(pdf_files) > 1:
        while True:
            try:
                choice = input(f"\nSelect a file (1-{len(pdf_files)}) or 'all' to process all files: ").strip()
                if choice.lower() == 'all':
                    selected_files = pdf_files
                    break
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(pdf_files):
                        selected_files = [pdf_files[choice_num - 1]]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(pdf_files)}")
            except ValueError:
                print("Please enter a valid number or 'all'")
    else:
        selected_files = pdf_files
        print(f"Processing: {os.path.basename(pdf_files[0])}")
    
    # Process each selected file
    all_transactions = []
    
    for pdf_path in selected_files:
        filename = os.path.basename(pdf_path)
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"{'='*60}")
        
        # Extract transactions
        transactions = extract_transactions_from_pdf(pdf_path)
        
        if not transactions:
            print(f"No transactions found in {filename}.")
            continue
        
        # Display transactions for this file
        print_transactions(transactions)
        
        # Show some basic stats for this file
        total_amount = sum(txn['amount'] for txn in transactions)
        debits = [txn for txn in transactions if txn['amount'] < 0]
        credits = [txn for txn in transactions if txn['amount'] > 0]
        
        print(f"\nSummary for {filename}:")
        print(f"Total transactions: {len(transactions)}")
        print(f"Debits: {len(debits)} (${sum(t['amount'] for t in debits):.2f})")
        print(f"Credits: {len(credits)} (${sum(t['amount'] for t in credits):.2f})")
        print(f"Net amount: ${total_amount:.2f}")
        
        # Add transactions to overall list
        all_transactions.extend(transactions)
    
    # If processing multiple files, show combined summary
    if len(selected_files) > 1:
        print(f"\n{'='*60}")
        print(f"COMBINED SUMMARY ({len(selected_files)} files)")
        print(f"{'='*60}")
        
        total_amount = sum(txn['amount'] for txn in all_transactions)
        debits = [txn for txn in all_transactions if txn['amount'] < 0]
        credits = [txn for txn in all_transactions if txn['amount'] > 0]
        
        print(f"Total transactions: {len(all_transactions)}")
        print(f"Debits: {len(debits)} (${sum(t['amount'] for t in debits):.2f})")
        print(f"Credits: {len(credits)} (${sum(t['amount'] for t in credits):.2f})")
        print(f"Net amount: ${total_amount:.2f}")
    
    # Use all_transactions for further processing
    transactions_to_process = all_transactions if len(selected_files) > 1 else transactions
    
    # Optional: Save to CSV
    save_to_csv = input("\nSave transactions to CSV? (y/n): ").lower().strip()
    if save_to_csv == 'y':
        if len(selected_files) == 1:
            filename = os.path.splitext(os.path.basename(selected_files[0]))[0] + "_transactions.csv"
        else:
            filename = "combined_transactions.csv"
        save_transactions_to_csv(transactions_to_process, filename)
    
    # Optional: Filter and group transactions
    filter_choice = input("\nFilter or group transactions? (y/n): ").lower().strip()
    if filter_choice == 'y':
        print("\nOptions:")
        print("1. Group all transactions by merchant")
        print("2. Show transaction details")
        
        choice = input("Choose option (1-2): ").strip()
        
        if choice == '1':
            merchant_totals = group_transactions_by_merchant(transactions_to_process)
            show_details = input("Show individual transaction details? (y/n): ").lower().strip() == 'y'
            print_grouped_transactions(merchant_totals, show_details)