from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from config import Config

def categorize_expense(description):
    """Categorize expense based on description"""
    description = description.lower()
    
    categories = {
        'Food': ['food', 'lunch', 'dinner', 'breakfast', 'snacks', 'coffee'],
        'Grocery': ['grocery', 'fruits', 'vegetables', 'supermarket'],
        'Transport': ['petrol', 'fuel', 'uber', 'taxi', 'bus', 'metro'],
        'Bills': ['bill', 'electricity', 'internet', 'phone', 'rent'],
        'Healthcare': ['medicine', 'doctor', 'hospital', 'medical'],
        'Entertainment': ['movie', 'games', 'entertainment'],
        'Others': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    
    return 'Others'

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store expenses in memory (replace with database in production)
expenses = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            if file.filename.endswith('.csv'):
                # Read CSV directly from the file object
                df = pd.read_csv(file)
                
                # Standardize column names
                df.columns = df.columns.str.strip().str.lower()
                
                if 'description' not in df.columns or 'amount' not in df.columns:
                    return jsonify({'error': 'CSV must have Description and Amount columns'}), 400
                
                # Process each row
                new_expenses = []
                for _, row in df.iterrows():
                    expense = {
                        'description': str(row['description']),
                        'amount': float(row['amount']),
                        'category': categorize_expense(str(row['description']))
                    }
                    new_expenses.append(expense)
                
                expenses.extend(new_expenses)
                return redirect(url_for('index'))
            
            else:  # Image file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                new_expenses = process_image(filepath)
                expenses.extend(new_expenses)
                return redirect(url_for('index'))
        
        except Exception as e:
            app.logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/manual', methods=['POST'])
def add_manual_expense():
    data = request.get_json()
    
    if not data or 'amount' not in data or 'description' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        amount = float(data['amount'])
        description = str(data['description'])
        
        from .utils.expense_processor import categorize_expense
        category = categorize_expense(description)
        
        expense = {
            'description': description,
            'amount': amount,
            'category': category
        }
        
        expenses.append(expense)
        return jsonify({'message': 'Expense added successfully'})
    
    except ValueError:
        return jsonify({'error': 'Invalid amount format'}), 400

@app.route('/api/expenses')
def get_expenses():
    return jsonify(expenses)

@app.route('/api/summary')
def get_summary():
    summary = {}
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        summary[category] = summary.get(category, 0) + amount
    
    return jsonify(summary)

@app.route('/api/clear', methods=['POST'])
def clear_expenses():
    expenses.clear()
    return jsonify({'message': 'All expenses cleared'})

if __name__ == '__main__':
    app.run(debug=True)