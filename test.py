from fastmcp import FastMCP
import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')

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
        c.execute('''
            INSERT INTO expenses (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, amount, category, subcategory, note))
        
        return {"status" : "ok", "id": c.lastrowid}
    

@mcp.tool
def list_expenses():
    '''List all expenses in the database.'''
    with sqlite3.connect(DB_PATH) as c:
        c.execute('SELECT * FROM expenses ORDER BY id ASC')
        cols = [description[0] for description in c.description]
        return [dict(zip(cols, row)) for row in c.fetchall()]
    

if __name__ == "__main__":
    mcp.run()