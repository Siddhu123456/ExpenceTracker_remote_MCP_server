from fastmcp import FastMCP
import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), 'categories.json')

mcp = FastMCP(name = 'ExpenseTracker')

def init_db():
    """Initialize the database and create the expenses table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as c:
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT "",
                note TEXT DEFAULT ""
            )
        ''')

init_db()

@mcp.tool
def add_expense(date, amount, category, subcategory="", note = ""):
    '''Add a new expense to the database.'''
    with sqlite3.connect(DB_PATH) as c:
        cursor = c.execute('''
            INSERT INTO expenses (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, amount, category, subcategory, note))
        
        return {"status" : "ok", "id": cursor.lastrowid}
    
@mcp.tool
def list_expenses(start_date, end_date):
    '''List all expenses in the database within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        cursor = c.execute('''
                  SELECT * 
                  FROM expenses 
                  WHERE date >= ? AND date <= ? 
                  ORDER BY id
                  ''', 
                  (start_date, end_date))
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    
@mcp.tool
def summarize(start_date, end_date, category = None):
    '''Summarize total expenses within an inclusive date range, optionally filtered by category.'''
    with sqlite3.connect(DB_PATH) as c:
        query = (
            '''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            '''
        )
        params = [start_date, end_date]
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' GROUP BY category ORDER BY category'
        
        cursor = c.execute(query, params)
        cols = [description[0] for description in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

@mcp.resource("expense://categories", mime_type = "application/json")
def categories():
    """Return the list of categories and subcategories as a JSON string."""
    with open(CATEGORIES_PATH, 'r', encoding = "utf-8") as f:
        return f.read()

if __name__ == "__main__":
    mcp.run(transport = "http", host = "0.0.0.0", port = 8000)