import pdfplumber
import re
from datetime import datetime

def extract_transactions_from_pdf(pdf_path):
    """Extract raw transaction data from PDF statement"""
    
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text() or ""
            all_text += "\n--- PAGE BREAK ---\n"
    
    # Headers to look for transaction sections
    headers = [
        "ATM/DebitCard transactionsthisstatementperiod",
        "ATM/DebitCard transactionsthisstatementperiod(continued)"
    ]
    
    # Stop at this section to avoid picking up other types of transactions
    stop_header = "Electronicwithdrawalsthisstatementperiod"
    stop_index = all_text.find(stop_header)
    if stop_index != -1:
        search_text = all_text[:stop_index]
    else:
        search_text = all_text
    
    # Extract transaction sections
    sections = []
    for header in headers:
        pattern = re.compile(rf"{header}(.*?)(\n[A-Z][A-Z /]+\n|--- PAGE BREAK ---|$)", re.DOTALL)
        matches = pattern.findall(search_text)
        for match in matches:
            section = match[0].strip()
            if section:
                sections.append(section)
    
    if not sections:
        print("ATM/Debit Card transactions section not found.")
        return []
    
    combined_section = "\n".join(sections)
    lines = [line.strip() for line in combined_section.splitlines() if line.strip()]
    
    # Parse individual transactions
    # Pattern: Date (e.g., Dec02) Amount (e.g., -45.67 or -1,526.13) Description
    transaction_pattern = re.compile(r"^(?P<date>[A-Za-z]{3}\d{2})\s+(?P<amount>-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(?P<description>.+)")
    
    transactions = []
    for line in lines:
        match = transaction_pattern.match(line)
        if match:
            date_str = match.group('date')
            amount_str = match.group('amount').replace(',', '')  # Remove commas before converting to float
            amount = float(amount_str)
            description = match.group('description').strip()
            
            transactions.append({
                'date': date_str,
                'amount': amount,
                'description': description,
                'raw_line': line
            })
    
    return transactions

def print_transactions(transactions):
    """Print transactions in a clean format"""
    if not transactions:
        print("No transactions found.")
        return
    
    print(f"\nFound {len(transactions)} transactions:")
    print("-" * 80)
    print(f"{'Date':<8} {'Amount':<12} {'Description'}")
    print("-" * 80)
    
    for txn in transactions:
        amount_str = f"${txn['amount']:.2f}"
        print(f"{txn['date']:<8} {amount_str:<12} {txn['description']}")

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

def filter_transactions(transactions, min_amount=None, max_amount=None, search_term=None):
    """Filter transactions based on criteria"""
    filtered = transactions
    
    if min_amount is not None:
        filtered = [t for t in filtered if abs(t['amount']) >= min_amount]
    
    if max_amount is not None:
        filtered = [t for t in filtered if abs(t['amount']) <= max_amount]
    
    if search_term:
        search_term = search_term.lower()
        filtered = [t for t in filtered if search_term in t['description'].lower()]
    
    return filtered

def group_transactions_by_merchant(transactions):
    """Group transactions by merchant and sum amounts"""
    from collections import defaultdict
    
    merchant_groups = defaultdict(list)
    
    for txn in transactions:
        # Extract merchant name (first word or first few words)
        description = txn['description']
        
        # Try to identify merchant patterns (check Uber BEFORE general * pattern)
        if 'Uber' in description or 'UberTrip' in description:
            # All Uber services (Uber, UberTrip, UberTechnologies)
            merchant = "Uber (All Services)"
        elif description.startswith('Qt'):
            # All QuikTrip locations
            merchant = "QuikTrip (All Locations)"
        elif description.startswith('Discount'):
            # Discount Tire
            merchant = "Discount Tire"
        elif '*' in description:
            # For services like "Lyft *1Ride12-29" 
            merchant = description.split('*')[0].strip()
        elif description.startswith('W/DAt'):
            # ATM withdrawals
            merchant = "ATM Withdrawal"
        elif 'Vehreg' in description:
            # Vehicle registration
            merchant = "Vehicle Registration"
        elif '.gov' in description:
            # Government services
            merchant = "Government Services"
        elif 'BankFee' in description or 'ATMUsageFee' in description:
            # Bank fees
            merchant = "Bank Fees"
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
    pdf_path = "Statements.pdf"
    
    # Extract transactions
    print("Extracting transactions from PDF...")
    transactions = extract_transactions_from_pdf(pdf_path)
    
    if not transactions:
        print("No transactions found. Check your PDF format or headers.")
        exit()
    
    # Display all transactions
    print_transactions(transactions)
    
    # Show some basic stats
    total_amount = sum(txn['amount'] for txn in transactions)
    debits = [txn for txn in transactions if txn['amount'] < 0]
    credits = [txn for txn in transactions if txn['amount'] > 0]
    
    print(f"\nSummary:")
    print(f"Total transactions: {len(transactions)}")
    print(f"Debits: {len(debits)} (${sum(t['amount'] for t in debits):.2f})")
    print(f"Credits: {len(credits)} (${sum(t['amount'] for t in credits):.2f})")
    print(f"Net amount: ${total_amount:.2f}")
    
    # Optional: Save to CSV
    save_to_csv = input("\nSave transactions to CSV? (y/n): ").lower().strip()
    if save_to_csv == 'y':
        save_transactions_to_csv(transactions)
    
    # Optional: Filter and group transactions
    filter_choice = input("\nFilter or group transactions? (y/n): ").lower().strip()
    if filter_choice == 'y':
        print("\nOptions:")
        print("1. Filter by search term")
        print("2. Group all transactions by merchant")
        print("3. Filter then group")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == '1':
            search_term = input("Search term: ").strip()
            if search_term:
                filtered = filter_transactions(transactions, search_term=search_term)
                print(f"\nFiltered results for '{search_term}':")
                print_transactions(filtered)
        
        elif choice == '2':
            merchant_totals = group_transactions_by_merchant(transactions)
            show_details = input("Show individual transaction details? (y/n): ").lower().strip() == 'y'
            print_grouped_transactions(merchant_totals, show_details)
        
        elif choice == '3':
            search_term = input("Search term for filtering: ").strip()
            if search_term:
                filtered = filter_transactions(transactions, search_term=search_term)
                print(f"\nFiltered results for '{search_term}':")
                print_transactions(filtered)
                
                group_filtered = input(f"\nGroup the {len(filtered)} filtered transactions? (y/n): ").lower().strip()
                if group_filtered == 'y':
                    merchant_totals = group_transactions_by_merchant(filtered)
                    show_details = input("Show individual transaction details? (y/n): ").lower().strip() == 'y'
                    print_grouped_transactions(merchant_totals, show_details)