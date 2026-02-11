from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory database - initialized with seed data
authors = [
    {
        "id": 1,
        "name": "Priya Sharma",
        "email": "priya@email.com",
        "bank_account": "1234567890",
        "ifsc": "HDFC0001234"
    },
    {
        "id": 2,
        "name": "Rahul Verma",
        "email": "rahul@email.com",
        "bank_account": "0987654321",
        "ifsc": "ICIC0005678"
    },
    {
        "id": 3,
        "name": "Anita Desai",
        "email": "anita@email.com",
        "bank_account": "5678901234",
        "ifsc": "SBIN0009012"
    }
]

books = [
    {"id": 1, "title": "The Silent River", "author_id": 1, "royalty_per_sale": 45},
    {"id": 2, "title": "Midnight in Mumbai", "author_id": 1, "royalty_per_sale": 60},
    {"id": 3, "title": "Code & Coffee", "author_id": 2, "royalty_per_sale": 75},
    {"id": 4, "title": "Startup Diaries", "author_id": 2, "royalty_per_sale": 50},
    {"id": 5, "title": "Poetry of Pain", "author_id": 2, "royalty_per_sale": 30},
    {"id": 6, "title": "Garden of Words", "author_id": 3, "royalty_per_sale": 40}
]

sales = [
    {"id": 1, "book_id": 1, "quantity": 25, "sale_date": "2025-01-05"},
    {"id": 2, "book_id": 1, "quantity": 40, "sale_date": "2025-01-12"},
    {"id": 3, "book_id": 2, "quantity": 15, "sale_date": "2025-01-08"},
    {"id": 4, "book_id": 3, "quantity": 60, "sale_date": "2025-01-03"},
    {"id": 5, "book_id": 3, "quantity": 45, "sale_date": "2025-01-15"},
    {"id": 6, "book_id": 4, "quantity": 30, "sale_date": "2025-01-10"},
    {"id": 7, "book_id": 5, "quantity": 20, "sale_date": "2025-01-18"},
    {"id": 8, "book_id": 6, "quantity": 10, "sale_date": "2025-01-20"}
]

withdrawals = []
withdrawal_id_counter = 1


# Helper function to find author by ID
def find_author(author_id):
    """Find and return an author by their ID"""
    return next((author for author in authors if author["id"] == author_id), None)


# Helper function to calculate total earnings for an author
def calculate_total_earnings(author_id):
    """Calculate total earnings from all book sales for an author"""
    author_books = [book for book in books if book["author_id"] == author_id]
    total_earnings = 0
    
    for book in author_books:
        book_sales = [sale for sale in sales if sale["book_id"] == book["id"]]
        total_sold = sum(sale["quantity"] for sale in book_sales)
        total_earnings += total_sold * book["royalty_per_sale"]
    
    return total_earnings


# Helper function to calculate current balance
def calculate_current_balance(author_id):
    """Calculate current balance (total earnings - withdrawals)"""
    total_earnings = calculate_total_earnings(author_id)
    author_withdrawals = [w for w in withdrawals if w["author_id"] == author_id]
    total_withdrawn = sum(w["amount"] for w in author_withdrawals)
    return total_earnings - total_withdrawn


# 1. GET /authors - List all authors with earnings and balance
@app.route('/authors', methods=['GET'])
def get_authors():
    """Get all authors with their financial summary"""
    authors_with_financials = []
    
    for author in authors:
        authors_with_financials.append({
            "id": author["id"],
            "name": author["name"],
            "total_earnings": calculate_total_earnings(author["id"]),
            "current_balance": calculate_current_balance(author["id"])
        })
    
    return jsonify(authors_with_financials)


# 2. GET /authors/<id> - Detailed author information with books
@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Get detailed information about a specific author"""
    author = find_author(author_id)
    
    if not author:
        return jsonify({"error": "Author not found"}), 404
    
    # Get all books by this author
    author_books = [book for book in books if book["author_id"] == author_id]
    
    # Calculate stats for each book
    books_with_stats = []
    for book in author_books:
        book_sales = [sale for sale in sales if sale["book_id"] == book["id"]]
        total_sold = sum(sale["quantity"] for sale in book_sales)
        total_royalty = total_sold * book["royalty_per_sale"]
        
        books_with_stats.append({
            "id": book["id"],
            "title": book["title"],
            "royalty_per_sale": book["royalty_per_sale"],
            "total_sold": total_sold,
            "total_royalty": total_royalty
        })
    
    total_earnings = calculate_total_earnings(author_id)
    current_balance = calculate_current_balance(author_id)
    
    return jsonify({
        "id": author["id"],
        "name": author["name"],
        "email": author["email"],
        "current_balance": current_balance,
        "total_earnings": total_earnings,
        "total_books": len(author_books),
        "books": books_with_stats
    })


# 3. GET /authors/<id>/sales - All sales for author's books
@app.route('/authors/<int:author_id>/sales', methods=['GET'])
def get_author_sales(author_id):
    """Get all sales for an author's books, sorted by date (newest first)"""
    author = find_author(author_id)
    
    if not author:
        return jsonify({"error": "Author not found"}), 404
    
    # Get all books by this author
    author_books = [book for book in books if book["author_id"] == author_id]
    author_book_ids = [book["id"] for book in author_books]
    
    # Get all sales for these books
    author_sales = []
    for sale in sales:
        if sale["book_id"] in author_book_ids:
            book = next(book for book in books if book["id"] == sale["book_id"])
            author_sales.append({
                "book_title": book["title"],
                "quantity": sale["quantity"],
                "royalty_earned": sale["quantity"] * book["royalty_per_sale"],
                "sale_date": sale["sale_date"]
            })
    
    # Sort by date, newest first
    author_sales.sort(key=lambda x: x["sale_date"], reverse=True)
    
    return jsonify(author_sales)


# 4. POST /withdrawals - Create withdrawal request
@app.route('/withdrawals', methods=['POST'])
def create_withdrawal():
    """Create a withdrawal request with validation"""
    data = request.get_json()
    
    # Validate request body
    if not data or "author_id" not in data or "amount" not in data:
        return jsonify({"error": "Missing required fields: author_id and amount"}), 400
    
    author_id = data["author_id"]
    amount = data["amount"]
    
    # Validate author exists
    author = find_author(author_id)
    if not author:
        return jsonify({"error": "Author not found"}), 404
    
    # Validate minimum withdrawal amount
    if amount < 500:
        return jsonify({"error": "Minimum withdrawal amount is ₹500"}), 400
    
    # Check current balance
    current_balance = calculate_current_balance(author_id)
    if amount > current_balance:
        return jsonify({
            "error": f"Insufficient balance. Current balance: ₹{current_balance}"
        }), 400
    
    # Create withdrawal record
    global withdrawal_id_counter
    withdrawal = {
        "id": withdrawal_id_counter,
        "author_id": author_id,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    withdrawal_id_counter += 1
    withdrawals.append(withdrawal)
    
    new_balance = current_balance - amount
    
    return jsonify({
        "id": withdrawal["id"],
        "author_id": withdrawal["author_id"],
        "amount": withdrawal["amount"],
        "status": withdrawal["status"],
        "created_at": withdrawal["created_at"],
        "new_balance": new_balance
    }), 201


# 5. GET /authors/<id>/withdrawals - Get all withdrawals for an author
@app.route('/authors/<int:author_id>/withdrawals', methods=['GET'])
def get_author_withdrawals(author_id):
    """Get all withdrawal requests for an author, sorted by date (newest first)"""
    author = find_author(author_id)
    
    if not author:
        return jsonify({"error": "Author not found"}), 404
    
    # Get all withdrawals for this author
    author_withdrawals = [w for w in withdrawals if w["author_id"] == author_id]
    
    # Sort by created_at, newest first
    author_withdrawals.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Format response
    formatted_withdrawals = [
        {
            "id": w["id"],
            "amount": w["amount"],
            "status": w["status"],
            "created_at": w["created_at"]
        }
        for w in author_withdrawals
    ]
    
    return jsonify(formatted_withdrawals)


# Root endpoint for testing
@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information"""
    return jsonify({
        "message": "BookLeaf Author Royalty API",
        "endpoints": [
            "GET /authors",
            "GET /authors/<id>",
            "GET /authors/<id>/sales",
            "POST /withdrawals",
            "GET /authors/<id>/withdrawals"
        ]
    })


# Run the application
if __name__ == '__main__':
    # Use PORT environment variable for deployment, default to 5000 for local
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)