import re
from datetime import datetime
from .base_parser import BankStatementParser

class ComericaParser(BankStatementParser):
    """Parser for Comerica Bank statements"""
    def detect_format(self):
        # Remove all spaces and check for key phrases
        text_no_spaces = self.all_text.replace(" ", "")
        return "BasicBusinessChecking" in text_no_spaces and "COMERICA" in self.all_text.upper()
    
    def extract_transactions(self):
        transactions = []
        
        # Extract statement period
        period_match = re.search(r"([A-Za-z]+)\s*(\d{1,2})\s*,\s*(\d{4})\s*to\s*([A-Za-z]+)\s*(\d{1,2})\s*,\s*(\d{4})", self.all_text)
        if period_match:
            statement_year = int(period_match.group(3))
            print(f"\nStatement period found, year: {statement_year}")
        else:
            statement_year = datetime.now().year
            print(f"\nUsing current year: {statement_year}")

        # Extract deposits
        deposits_section = re.search(r"Paper depositsthisstatementperiod.*?(?=Transfer from|Electronic withdrawals|$)", self.all_text, re.DOTALL)
        if deposits_section:
            print("\nProcessing deposits section...")
            deposits_text = deposits_section.group(0)
            # Pattern: Apr10 1,000.00 0320146555
            deposit_pattern = r"([A-Z][a-z]{2})(\d{1,2})\s+([\d,]+\.\d{2})\s+(\d+)"
            for match in re.finditer(deposit_pattern, deposits_text):
                month, day, amount_str, ref_num = match.groups()
                amount = float(amount_str.replace(',', ''))
                date_str = f"{month} {day}, {statement_year}"
                transactions.append({
                    'date': date_str,
                    'amount': amount,
                    'description': f"Paper Deposit Ref:{ref_num}",
                    'type': 'deposit'
                })
                print(f"Found deposit: {date_str} - ${amount:.2f}")

        # Extract transfers
        transfers_section = re.search(r"Transferfrom otheraccountsthisstatementperiod.*?(?=Electronicwithdrawalsthisstatementperiod|$)", self.all_text, re.DOTALL)
        if transfers_section:
            print("\nProcessing transfers section...")
            transfers_text = transfers_section.group(0)
            # Pattern: Apr18 190.00 WebFundsTransferFromAccount Xxxxxx6649 WB10409873
            transfer_pattern = r"([A-Z][a-z]{2})(\d{1,2})\s+([\d,]+\.\d{2})\s+(.*?)\s+(\w+)\s+(\w+)"
            for match in re.finditer(transfer_pattern, transfers_text):
                month, day, amount_str, activity, account, ref_num = match.groups()
                amount = float(amount_str.replace(',', ''))
                date_str = f"{month} {day}, {statement_year}"
                transactions.append({
                    'date': date_str,
                    'amount': amount,
                    'description': f"{activity} {account} Ref:{ref_num}",
                    'type': 'transfer'
                })
                print(f"Found transfer: {date_str} - ${amount:.2f}")

        # Extract withdrawals
        withdrawals_section = re.search(r"Electronicwithdrawalsthisstatementperiod.*?(?=Fees and|$)", self.all_text, re.DOTALL)
        if withdrawals_section:
            print("\nProcessing withdrawals section...")
            withdrawals_text = withdrawals_section.group(0)
            
            # Pattern for all electronic withdrawals: Date Amount Activity Reference
            # This should catch all electronic withdrawals except fees
            withdrawal_pattern = r"([A-Z][a-z]{2})(\d{1,2})\s+(-?[\d,]+\.\d{2})\s+(.*?)\s+(\w+)"
            for match in re.finditer(withdrawal_pattern, withdrawals_text):
                month, day, amount_str, activity, ref_num = match.groups()
                amount = float(amount_str.replace(',', ''))
                date_str = f"{month} {day}, {statement_year}"
                
                # Skip fee transactions - they should be captured in the fees section
                if 'Fee-' in activity or 'ServiceCharge' in activity:
                    continue
                
                # Determine transaction type based on activity description
                if 'Wire' in activity:
                    txn_type = 'wire_transfer'
                    print(f"Found wire transfer: {date_str} - ${amount:.2f}")
                elif 'Zelle' in activity:
                    txn_type = 'zelle'
                    print(f"Found Zelle transaction: {date_str} - ${amount:.2f}")
                elif 'Wf Payment' in activity or 'Wf' in activity:
                    txn_type = 'wells_fargo_payment'
                    print(f"Found Wells Fargo payment: {date_str} - ${amount:.2f}")
                elif 'Toyota' in activity:
                    txn_type = 'toyota_payment'
                    print(f"Found Toyota payment: {date_str} - ${amount:.2f}")
                elif 'Ally' in activity:
                    txn_type = 'ally_payment'
                    print(f"Found Ally payment: {date_str} - ${amount:.2f}")
                elif 'GMFinancial' in activity:
                    txn_type = 'gm_financial_payment'
                    print(f"Found GM Financial payment: {date_str} - ${amount:.2f}")
                elif 'FordMotor' in activity:
                    txn_type = 'ford_payment'
                    print(f"Found Ford payment: {date_str} - ${amount:.2f}")
                elif 'TdAutoFinance' in activity:
                    txn_type = 'td_auto_payment'
                    print(f"Found TD Auto payment: {date_str} - ${amount:.2f}")
                elif 'Bridgecrest' in activity:
                    txn_type = 'bridgecrest_payment'
                    print(f"Found Bridgecrest payment: {date_str} - ${amount:.2f}")
                else:
                    txn_type = 'other_withdrawal'
                    print(f"Found other withdrawal: {date_str} - ${amount:.2f}")
                
                transactions.append({
                    'date': date_str,
                    'amount': amount,
                    'description': f"{activity} Ref:{ref_num}",
                    'type': txn_type
                })

        # Extract fees
        fees_section = re.search(r"Feesandservice chargesthisstatementperiod.*?(?=Lowest daily|$)", self.all_text, re.DOTALL)
        if fees_section:
            print("\nProcessing fees section...")
            fees_text = fees_section.group(0)
            # Pattern: Apr17 -26.00 Fee-ReturnedItem 0970314433
            fee_pattern = r"([A-Z][a-z]{2})(\d{1,2})\s+(-?[\d,]+\.\d{2})\s+(.*?)\s+(\d+)"
            for match in re.finditer(fee_pattern, fees_text):
                month, day, amount_str, activity, ref_num = match.groups()
                amount = float(amount_str.replace(',', ''))
                date_str = f"{month} {day}, {statement_year}"
                
                # Determine fee type
                if 'Fee-Overdraft' in activity:
                    fee_type = 'overdraft_fee'
                    print(f"Found overdraft fee: {date_str} - ${amount:.2f}")
                elif 'Fee-ReturnedItem' in activity:
                    fee_type = 'returned_item_fee'
                    print(f"Found returned item fee: {date_str} - ${amount:.2f}")
                elif 'ServiceCharge' in activity:
                    fee_type = 'service_charge'
                    print(f"Found service charge: {date_str} - ${amount:.2f}")
                else:
                    fee_type = 'other_fee'
                    print(f"Found other fee: {date_str} - ${amount:.2f}")
                
                transactions.append({
                    'date': date_str,
                    'amount': amount,
                    'description': f"{activity} Ref:{ref_num}",
                    'type': fee_type
                })

        # Remove duplicates based on date, amount, and description
        seen = set()
        unique_transactions = []
        for txn in transactions:
            key = (txn['date'], txn['amount'], txn['description'])
            if key not in seen:
                seen.add(key)
                unique_transactions.append(txn)

        # Sort transactions by date
        unique_transactions.sort(key=lambda x: datetime.strptime(x['date'], '%b %d, %Y'))
        
        print(f"\nTotal transactions found: {len(unique_transactions)}")
        return unique_transactions