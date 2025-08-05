import pdfplumber
import re
import os
import glob
from datetime import datetime

class BankStatementParser:
    """Base class for bank statement parsers"""
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        with pdfplumber.open(pdf_path) as pdf:
            self.all_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                self.all_text += page_text
                self.all_text += "\n--- PAGE BREAK ---\n"
    
    def detect_format(self):
        """Detect the format of the bank statement"""
        raise NotImplementedError
    
    def extract_transactions(self):
        """Extract transactions from the bank statement"""
        raise NotImplementedError

class ProsperityBankParser(BankStatementParser):
    """Parser for Prosperity Bank statements"""
    def detect_format(self):
        return "STATEMENT SUMMARY" in self.all_text and "DEPOSITS/OTHER CREDITS" in self.all_text
    
    def extract_transactions(self):
        sections = []
        
        # Find all sections between "DEPOSITS/OTHER CREDITS" and the next section
        deposits_pattern = re.compile(r"DEPOSITS/OTHER CREDITS\s*Date\s*Description\s*Amount(.*?)(?:OTHER DEBITS|CHECKS|SERVICE CHARGE SUMMARY|--- PAGE BREAK ---|$)", re.DOTALL)
        deposits_matches = deposits_pattern.finditer(self.all_text)
        
        # Find all sections between "OTHER DEBITS" and the next section
        debits_pattern = re.compile(r"OTHER DEBITS\s*Date\s*Description\s*Amount(.*?)(?:DEPOSITS/OTHER CREDITS|CHECKS|SERVICE CHARGE SUMMARY|--- PAGE BREAK ---|$)", re.DOTALL)
        debits_matches = debits_pattern.finditer(self.all_text)
        
        # Process deposits and debits
        for match in deposits_matches:
            section = match.group(1).strip()
            if section:
                sections.append(("deposit", section))
        
        for match in debits_matches:
            section = match.group(1).strip()
            if section:
                sections.append(("debit", section))
        
        if not sections:
            print("No transaction sections found.")
            return []
        
        transactions = []
        for section_type, section in sections:
            lines = [line.strip() for line in section.splitlines() if line.strip()]
            for line in lines:
                # Pattern: Date (MM/DD/YYYY) Description Amount
                match = re.match(r"(?P<date>\d{2}/\d{2}/\d{4})\s+(?P<description>.*?)\s+\$?(?P<amount>-?\d{1,3}(?:,\d{3})*\.\d{2})\s*$", line)
                if match:
                    date_str = match.group('date')
                    description = match.group('description').strip()
                    amount_str = match.group('amount').replace(',', '')
                    amount = float(amount_str)
                    if section_type == "debit":
                        amount = -abs(amount)
                    else:
                        amount = abs(amount)
                    
                    transactions.append({
                        'date': date_str,
                        'amount': amount,
                        'description': description,
                        'raw_line': line
                    })
        
        return transactions

class ChaseParser(BankStatementParser):
    """Parser for Chase Bank statements"""
    def detect_format(self):
        return "CHASE" in self.all_text.upper() and "ACCOUNT ACTIVITY" in self.all_text.upper()
    
    def extract_transactions(self):
        transactions = []
        # Find the transaction section
        activity_pattern = re.compile(r"ACCOUNT ACTIVITY.*?(?:DAILY ENDING BALANCE|ANNUAL PERCENTAGE YIELD|$)", re.DOTALL)
        match = activity_pattern.search(self.all_text)
        
        if not match:
            print("No transaction section found.")
            return []
            
        section = match.group(0)
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        
        # Pattern: MM/DD Description Amount Balance
        for line in lines:
            match = re.match(r"(?P<date>\d{2}/\d{2})\s+(?P<description>.*?)\s+(?P<amount>-?\$?\d{1,3}(?:,\d{3})*\.\d{2})", line)
            if match:
                date_str = match.group('date')
                description = match.group('description').strip()
                amount_str = match.group('amount').replace('$', '').replace(',', '')
                amount = float(amount_str)
                
                transactions.append({
                    'date': f"{date_str}/2024",  # Add year from statement
                    'amount': amount,
                    'description': description,
                    'raw_line': line
                })
        
        return transactions

class WellsFargoParser(BankStatementParser):
    """Parser for Wells Fargo statements"""
    def detect_format(self):
        return "WELLS FARGO" in self.all_text.upper() and "TRANSACTION HISTORY" in self.all_text.upper()
    
    def extract_transactions(self):
        transactions = []
        # Find the transaction section
        history_pattern = re.compile(r"TRANSACTION HISTORY.*?(?:MONTHLY SERVICE FEE SUMMARY|IMPORTANT ACCOUNT INFORMATION|$)", re.DOTALL)
        match = history_pattern.search(self.all_text)
        
        if not match:
            print("No transaction section found.")
            return []
            
        section = match.group(0)
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        
        # Pattern: MM/DD Description Amount
        for line in lines:
            match = re.match(r"(?P<date>\d{1,2}/\d{1,2})\s+(?P<description>.*?)\s+(?P<amount>-?\$?\d{1,3}(?:,\d{3})*\.\d{2})", line)
            if match:
                date_str = match.group('date')
                description = match.group('description').strip()
                amount_str = match.group('amount').replace('$', '').replace(',', '')
                amount = float(amount_str)
                
                transactions.append({
                    'date': f"{date_str}/2024",  # Add year from statement
                    'amount': amount,
                    'description': description,
                    'raw_line': line
                })
        
        return transactions

def extract_transactions_from_pdf(pdf_path):
    """Extract raw transaction data from PDF statement"""
    parsers = [
        ProsperityBankParser,
        ChaseParser,
        WellsFargoParser
    ]
    
    # Try each parser until we find one that works
    for parser_class in parsers:
        parser = parser_class(pdf_path)
        if parser.detect_format():
            print(f"Detected format: {parser_class.__name__}")
            return parser.extract_transactions()
    
    print("Unknown bank statement format. Please implement a new parser for this format.")
    return []
    
    transactions = []
    for line in lines:
        match = transaction_pattern.match(line)
        if match:
            date_str = match.group('date')
            description = match.group('description').strip()
            amount_str = match.group('amount').replace(',', '')  # Remove commas before converting to float
            
            # Convert amount to float and make debits negative
            amount = float(amount_str)
            if "OTHER DEBITS" in line or amount < 0:
                amount = -abs(amount)  # Ensure negative for debits
            else:
                amount = abs(amount)  # Ensure positive for credits
            
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
    # Look for PDF files in the statements directory
    statements_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "statements")  # Absolute path to statements directory
    pdf_files = glob.glob(os.path.join(statements_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {statements_dir} directory.")
        print("Please place your bank statement PDF files in the statements/ directory.")
        exit()
    
    # If multiple PDF files found, let user choose
    if len(pdf_files) > 1:
        print("Multiple PDF files found:")
        for i, pdf_file in enumerate(pdf_files, 1):
            filename = os.path.basename(pdf_file)
            print(f"{i}. {filename}")
        
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
        print("Extracting transactions from PDF...")
        transactions = extract_transactions_from_pdf(pdf_path)
        
        if not transactions:
            print(f"No transactions found in {filename}. Check your PDF format or headers.")
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
        print("1. Filter by search term")
        print("2. Group all transactions by merchant")
        print("3. Filter then group")
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == '1':
            search_term = input("Search term: ").strip()
            if search_term:
                filtered = filter_transactions(transactions_to_process, search_term=search_term)
                print(f"\nFiltered results for '{search_term}':")
                print_transactions(filtered)
        
        elif choice == '2':
            merchant_totals = group_transactions_by_merchant(transactions_to_process)
            show_details = input("Show individual transaction details? (y/n): ").lower().strip() == 'y'
            print_grouped_transactions(merchant_totals, show_details)
        
        elif choice == '3':
            search_term = input("Search term for filtering: ").strip()
            if search_term:
                filtered = filter_transactions(transactions_to_process, search_term=search_term)
                print(f"\nFiltered results for '{search_term}':")
                print_transactions(filtered)
                
                group_filtered = input(f"\nGroup the {len(filtered)} filtered transactions? (y/n): ").lower().strip()
                if group_filtered == 'y':
                    merchant_totals = group_transactions_by_merchant(filtered)
                    show_details = input("Show individual transaction details? (y/n): ").lower().strip() == 'y'
                    print_grouped_transactions(merchant_totals, show_details)