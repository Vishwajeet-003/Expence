import pandas as pd
import cv2
import pytesseract
import re
from PIL import Image

def process_csv(file_path):
    """Process CSV file and extract expenses"""
    try:
        df = pd.read_csv(file_path)
        
        # Try to identify amount and description columns
        possible_amount_cols = ['amount', 'price', 'cost', 'value']
        possible_desc_cols = ['description', 'item', 'name', 'details']
        
        amount_col = None
        desc_col = None
        
        # Find amount column
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in possible_amount_cols:
                amount_col = col
                break
        
        # Find description column
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in possible_desc_cols:
                desc_col = col
                break
        
        if not amount_col or not desc_col:
            raise ValueError("Could not identify amount and description columns")
        
        # Extract expenses
        expenses = []
        for _, row in df.iterrows():
            amount = float(row[amount_col])
            description = str(row[desc_col])
            category = categorize_expense(description)
            
            expenses.append({
                'description': description,
                'amount': amount,
                'category': category
            })
        
        return expenses
    
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

def process_image(image_path):
    """Extract text from receipt image using OCR"""
    try:
        # Read image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply OCR
        text = pytesseract.image_to_string(thresh)
        
        # Extract amounts and descriptions using regex
        amounts = re.findall(r'\$?(\d+\.\d{2})', text)
        lines = text.split('\n')
        
        expenses = []
        for line in lines:
            # Look for amount patterns in each line
            amount_match = re.search(r'\$?(\d+\.\d{2})', line)
            if amount_match:
                amount = float(amount_match.group(1))
                # Get description by removing the amount and any extra whitespace
                description = re.sub(r'\$?\d+\.\d{2}', '', line).strip()
                
                if description and amount > 0:
                    category = categorize_expense(description)
                    expenses.append({
                        'description': description,
                        'amount': amount,
                        'category': category
                    })
        
        return expenses
    
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def categorize_expense(description):
    """Categorize expense based on description"""
    description = description.lower()
    
    categories = {
        'Food': ['restaurant', 'cafe', 'food', 'pizza', 'burger', 'meal'],
        'Grocery': ['grocery', 'supermarket', 'mart', 'vegetables', 'fruits'],
        'Transport': ['uber', 'taxi', 'bus', 'metro', 'fuel', 'petrol'],
        'Shopping': ['amazon', 'flipkart', 'clothing', 'shoes', 'electronics'],
        'Entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'game'],
        'Bills': ['electricity', 'water', 'internet', 'phone', 'rent'],
        'Healthcare': ['hospital', 'pharmacy', 'medicine', 'doctor'],
        'Others': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in description for keyword in keywords):
            return category
    
    return 'Others'