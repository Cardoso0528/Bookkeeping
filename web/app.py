from flask import Flask, render_template, jsonify
import os
import sys
from datetime import datetime

# Add parent directory to path so we can import parsers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers import AVAILABLE_PARSERS

app = Flask(__name__)

def get_statements():
    """Get list of statements from statements directory"""
    statements_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "statements")
    pdf_files = []
    
    for file in os.listdir(statements_dir):
        if file.endswith('.pdf'):
            path = os.path.join(statements_dir, file)
            size = os.path.getsize(path) / 1024  # Convert to KB
            mtime = os.path.getmtime(path)
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            pdf_files.append({
                'name': file,
                'path': path,
                'size': f"{size:.1f}KB",
                'modified': mtime_str
            })
    
    # Sort by modified time (newest first)
    pdf_files.sort(key=lambda x: x['modified'], reverse=True)
    return pdf_files

def process_statement(path):
    """Process a single statement and return transactions with detailed analysis"""
    for parser_class in AVAILABLE_PARSERS:
        parser = parser_class(path)
        if parser.detect_format():
            transactions = parser.extract_transactions()
            
            # Basic summary
            total_amount = sum(t['amount'] for t in transactions)
            debits = [t for t in transactions if t['amount'] < 0]
            credits = [t for t in transactions if t['amount'] > 0]
            
            # Detailed analysis
            deposits = [t for t in transactions if t['amount'] > 0]
            paper_deposits = [t for t in deposits if 'Paper Deposit' in t['description']]
            
            # Electronic withdrawals
            wire_transfers = [t for t in transactions if 'Wire#' in t['description']]
            toyota_payments = [t for t in transactions if 'Toyota' in t['description']]
            gm_payments = [t for t in transactions if 'GMFinancial' in t['description']]
            ford_payments = [t for t in transactions if 'FordMotor' in t['description']]
            ally_payments = [t for t in transactions if 'Ally' in t['description']]
            td_payments = [t for t in transactions if 'TdAutoFinance' in t['description']]
            bridgecrest_payments = [t for t in transactions if 'Bridgecrest' in t['description']]
            wf_payments = [t for t in transactions if 'Wf Payment' in t['description']]
            
            # Checks
            check_transactions = [t for t in transactions if 'Checks' in t['description']]
            
            # Fees
            service_charges = [t for t in transactions if 'ServiceCharge' in t['description']]
            returned_item_fees = [t for t in transactions if 'Fee-ReturnedItem' in t['description']]
            overdraft_fees = [t for t in transactions if 'Fee-Overdraft' in t['description']]
            
            def category_summary(transactions):
                return {
                    'count': len(transactions),
                    'total': sum(t['amount'] for t in transactions),
                    'transactions': transactions
                }
            
            return {
                'format': parser_class.__name__,
                'transactions': transactions,
                'summary': {
                    'total_transactions': len(transactions),
                    'total_amount': total_amount,
                    'total_debits': len(debits),
                    'total_credits': len(credits),
                    'debit_amount': sum(t['amount'] for t in debits),
                    'credit_amount': sum(t['amount'] for t in credits)
                },
                'detailed_analysis': {
                    'deposits': {
                        'all': category_summary(deposits),
                        'paper': category_summary(paper_deposits)
                    },
                    'electronic_withdrawals': {
                        'wire_transfers': category_summary(wire_transfers),
                        'auto_payments': {
                            'toyota': category_summary(toyota_payments),
                            'gm_financial': category_summary(gm_payments),
                            'ford': category_summary(ford_payments),
                            'ally': category_summary(ally_payments),
                            'td_auto': category_summary(td_payments),
                            'bridgecrest': category_summary(bridgecrest_payments),
                            'wells_fargo': category_summary(wf_payments)
                        }
                    },
                    'checks': category_summary(check_transactions),
                    'fees': {
                        'service_charges': category_summary(service_charges),
                        'returned_item_fees': category_summary(returned_item_fees),
                        'overdraft_fees': category_summary(overdraft_fees)
                    }
                }
            }
    
    return None

@app.route('/')
def index():
    """Main page - show list of statements"""
    statements = get_statements()
    return render_template('index.html', statements=statements)

@app.route('/statement/<path:filename>')
def statement_details(filename):
    """Show details for a single statement"""
    statements_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "statements")
    path = os.path.join(statements_dir, filename)
    
    if not os.path.exists(path):
        return "Statement not found", 404
    
    result = process_statement(path)
    if not result:
        return "Could not process statement", 400
    
    return render_template('statement.html', 
                         filename=filename,
                         format=result['format'],
                         transactions=result['transactions'],
                         summary=result['summary'],
                         detailed_analysis=result['detailed_analysis'])

@app.route('/api/statement/<path:filename>')
def statement_api(filename):
    """API endpoint for statement data"""
    statements_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "statements")
    path = os.path.join(statements_dir, filename)
    
    if not os.path.exists(path):
        return jsonify({'error': 'Statement not found'}), 404
    
    result = process_statement(path)
    if not result:
        return jsonify({'error': 'Could not process statement'}), 400
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)