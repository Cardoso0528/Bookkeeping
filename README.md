Transaction Extractor

A Python tool for extracting and analyzing transactions from PDF bank statements. This tool helps you understand your spending patterns by grouping transactions by merchant and providing detailed analysis.

Features:
    Extract transactions from PDF bank statements
    Group by merchant with intelligent categorization
    Calculate totals and averages for each merchant
    Filter transactions by search terms
    Export to CSV for further analysis
    Smart grouping combines related merchants (e.g., all Uber services, all QuikTrip locations)
    Handles edge cases like comma-separated amounts

Requirements:
    Python 3.x
    `pdfplumber` library

Installation:
    Clone or download this repository
    Install required dependencies:
        pip install pdfplumber

Use: 
1. Place your PDF bank statement in the same directory as `extraction.py`
2. Update the `pdf_path` variable in the script to match your PDF filename:
   ```python
   pdf_path = "your_statement.pdf"
   ```
3. Run the script:
   ```bash
   python3 extraction.py
   ```

