import pdfplumber

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