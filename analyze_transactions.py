from collections import defaultdict
from datetime import datetime
import re

def parse_transaction(line):
    # Pattern: Date Amount Description
    match = re.match(r'(\w+)(\d{2})\s+(-?\d+,?\d*\.\d{2})\s+(.+)', line)
    if match:
        month, day, amount, description = match.groups()
        amount = float(amount.replace(',', ''))
        return {
            'date': f"{month}{day}",
            'amount': amount,
            'description': description,
            'merchant': extract_merchant(description)
        }
    return None

def extract_merchant(description):
    # Extract the main merchant name before location
    parts = description.split(' ')
    if len(parts) >= 2:
        if parts[0].lower() in ['the', 'a', 'an']:
            return ' '.join(parts[:2])
        return parts[0]
    return description

def analyze_transactions(transactions):
    # Group by merchant
    merchant_totals = defaultdict(lambda: {'count': 0, 'total': 0.0, 'transactions': []})
    
    for txn in transactions:
        merchant = txn['merchant']
        merchant_totals[merchant]['count'] += 1
        merchant_totals[merchant]['total'] += txn['amount']
        merchant_totals[merchant]['transactions'].append(txn)
    
    # Sort merchants by total spend (absolute value)
    sorted_merchants = sorted(
        merchant_totals.items(),
        key=lambda x: abs(x[1]['total']),
        reverse=True
    )
    
    # Calculate overall totals
    total_spend = sum(t['amount'] for t in transactions)
    total_count = len(transactions)
    
    return {
        'merchants': sorted_merchants,
        'total_spend': total_spend,
        'total_count': total_count
    }

def print_summary(analysis):
    print("\nTransaction Summary")
    print("=" * 80)
    print(f"Total Transactions: {analysis['total_count']}")
    print(f"Total Amount: ${analysis['total_spend']:.2f}")
    print("\nBreakdown by Merchant:")
    print("-" * 80)
    print(f"{'Merchant':<30} {'Count':>8} {'Total':>12} {'Avg/Trans':>12}")
    print("-" * 80)
    
    for merchant, data in analysis['merchants']:
        count = data['count']
        total = data['total']
        avg = total / count
        print(f"{merchant[:30]:<30} {count:>8} ${total:>10.2f} ${avg:>10.2f}")
    
    print("-" * 80)

def main():
    # Read transactions from input
    print("Enter transactions (one per line, blank line to finish):")
    transactions = []
    while True:
        try:
            line = input().strip()
            if not line:
                break
            txn = parse_transaction(line)
            if txn:
                transactions.append(txn)
        except EOFError:
            break
    
    # Analyze and print summary
    analysis = analyze_transactions(transactions)
    print_summary(analysis)
    
    # Ask if user wants to see transaction details for specific merchant
    while True:
        print("\nEnter merchant name to see details (or press Enter to exit):")
        merchant = input().strip()
        if not merchant:
            break
        
        # Find merchant (case-insensitive)
        for m, data in analysis['merchants']:
            if m.lower() == merchant.lower():
                print(f"\nTransactions for {m}:")
                print("-" * 80)
                print(f"{'Date':<10} {'Amount':>10} {'Description'}")
                print("-" * 80)
                for txn in data['transactions']:
                    print(f"{txn['date']:<10} ${txn['amount']:>9.2f} {txn['description']}")
                print("-" * 80)
                print(f"Total: ${data['total']:.2f} ({data['count']} transactions)")
                break
        else:
            print("Merchant not found.")

if __name__ == "__main__":
    main()