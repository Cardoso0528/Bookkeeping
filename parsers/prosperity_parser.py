import re
from datetime import datetime
from .base_parser import BankStatementParser

class ProsperityParser(BankStatementParser):
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
        
        # Sort transactions by date
        transactions.sort(key=lambda x: datetime.strptime(x['date'], '%m/%d/%Y'))
        return transactions