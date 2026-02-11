# BookLeaf Author Royalty API

## Live Deployment
**API URL**: https://bookleaf-royalty-api-udj9.onrender.com

## Tech Stack
**Python with Flask** - Chosen for its simplicity, lightweight nature, and excellent support for building REST APIs quickly. Flask's minimalist approach made it easy to focus on implementing the business logic correctly.

**In-memory storage** - As per requirements, using Python dictionaries and lists for data storage.

## API Endpoints

- `GET /authors` - List all authors with earnings and balance
- `GET /authors/<id>` - Detailed author information with books
- `GET /authors/<id>/sales` - All sales for an author's books
- `POST /withdrawals` - Create withdrawal request
- `GET /authors/<id>/withdrawals` - Get all withdrawals for an author

## Testing Locally
```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000/authors

## Assumptions Made

1. All monetary amounts are in INR (₹)
2. Dates are in YYYY-MM-DD format
3. Data is stored in-memory (resets on server restart)
4. Withdrawal status is always "pending" upon creation
5. Author IDs, book IDs, and sale IDs are unique integers

## Time Spent

Approximately **[3 hours]** - including:
- Understanding requirements: ~30 min
- Building and testing API: ~[1 hours]
- Deployment and debugging: ~[1 hours]

## Validation Rules Implemented

- Minimum withdrawal: ₹500
- Cannot withdraw more than current balance
- All required fields validated
- Proper HTTP status codes (200, 201, 400, 404)
- CORS enabled for cross-origin requests