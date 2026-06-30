import datetime
import logging
import sqlite3
import sys

logging.basicConfig(
    filename="activity_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

expenses = []
current_user = ""
current_user_id = None

def init_db():
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses( 
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()
         
def login_user():
    global current_user, current_user_id
    name = input("Enter your username to login: ").strip().lower()
    
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username) values (?);", (name,))
    conn.commit()
    
    cursor.execute("SELECT id FROM users WHERE username = ?;", (name,))
    result = cursor.fetchone()
    current_user = name
    current_user_id = result[0]
    
    print(f"\nWelcome, {current_user.capitalize()}! Your Database ID is: {current_user_id}")
    
    logging.info(f"User '{current_user}' successfully logged in (Database ID: {current_user_id})")
    conn.close()

def load_expenses():
    global expenses
    expenses.clear()
    
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT amount, category, description FROM expenses WHERE user_id = ?;", (current_user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        expenses.append({
            "amount": row[0],
            "category": row[1],
            "description": row[2]
        })
    print("Your history has been safely loaded from the master ledger database grid.")
    
    logging.info(f"Loaded {len(expenses)} records into memory for user id: {current_user_id}")

def get_valid_amount():
    while True:
        try:
            amt = float(input("Enter the amount: "))
            if amt >= 0:
                return amt   
            else:
                print(f"{amt} is invalid.")
        except ValueError:
            print("Invalid number. Please enter digits only.")  

def add_expenses():
    amt = get_valid_amount()
    cat = input("Select category (food, travel, etc): ").strip()
    des = input("Description: ").strip()
    
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, description, user_id) VALUES (?, ?, ?, ?);", (amt, cat, des, current_user_id))
    conn.commit()
    conn.close()

    expenses.append({
        "amount": amt, 
        "category": cat,
        "description": des
    })
    
    print("Expense logged safely into your live ledger rows!")
    logging.info(f"EXPENSE ADDED: User '{current_user}' added {amt} in '{cat}'.")

def view_expenses():
    if not expenses:
        print("Your memory tracker is empty.")
        return
    print("\n--- Current Memory Clipboard View ---")
    for items in expenses:
        print(f"Amount: {items['amount']} | Category: {items['category']} | Description: {items['description']}")

def view_all_db_receipts():
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, category, description FROM expenses WHERE user_id = ?;", (current_user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No master database receipts found.")
    else:
        print("\n--- Your Active Database Receipts ---")
        for row in rows:
            print(f"Receipt ID: {row[0]} | Amount: {row[1]} | Category: {row[2]} | Description: {row[3]}")

def delete_expenses():
    global expenses
    view_all_db_receipts()
    
    receipt_id = input("\nEnter the Receipt ID you want to delete: ").strip()
    if not receipt_id:
        return

    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
     
    cursor.execute("SELECT amount, category, description FROM expenses WHERE id = ? AND user_id = ?;", (receipt_id, current_user_id))
    matched_row = cursor.fetchone()
    
    if matched_row:
        amt_to_remove = matched_row[0]
        cat_to_remove = matched_row[1]  
        des_to_remove = matched_row[2]
        
        cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?;", (receipt_id, current_user_id))
        conn.commit()
        
        logging.info(f"User '{current_user}' deleted receipt #{receipt_id} (Amount: {amt_to_remove}, Category: {cat_to_remove})")
        conn.close()
        print(f"Receipt #{receipt_id} deleted successfully from database grid!")
        
        for item in expenses:
            if item["amount"] == amt_to_remove and item["category"] == cat_to_remove and item["description"] == des_to_remove:
                expenses.remove(item)
                break
    else:
        print(f"No matching receipt found with ID {receipt_id} for deletion.")
        conn.close()

def view_sorted_expenses():
    if not expenses:
        print("Your tracker is empty.")
        return 
    
    print("How would you like to sort?")
    print("1. Ascending order")
    print("2. Descending order")
    order = input("Enter choice (1-2): ").strip()

    if order == "1":
        expenses.sort(key=lambda item: item["amount"])
        print("\nExpenses (Lowest to Highest):")
    elif order == "2":
        expenses.sort(key=lambda items: items["amount"], reverse=True)
        print("\nExpenses (Highest to Lowest):")
    else:
        print("Invalid choice. Showing unsorted data:")
        
    for items in expenses:
        print(f"Amount: {items['amount']} | Category: {items['category']} | Description: {items['description']}")

def total_spending():
    total = sum(items["amount"] for items in expenses)
    print(f"Total Spending: {total}")

def category_summary():
    summary = {}
    for items in expenses:
        cat = items["category"]
        amt = items["amount"]
        summary[cat] = summary.get(cat, 0) + amt
        
    print("\n--- Category Summary ---")
    for cat, total in summary.items():
        print(f"{cat}: {total}")

def get_menu_choice(max_choice=8):
    while True:
        choice = input(f"Enter your choice (1-{max_choice}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= max_choice:
            return int(choice)  
        else:
            print("Invalid choice, try again!")

def exit_program():
    print("Exiting Intel Tracker. Goodbye!")
    sys.exit()

def main():
    init_db()
    print("Welcome To Intel Tracker")
   
    login_user()
    load_expenses()
    
    menu_actions = {
        1: add_expenses,
        2: view_expenses,
        3: view_sorted_expenses,
        4: total_spending,
        5: category_summary,
        6: delete_expenses,
        7: view_all_db_receipts,
        8: exit_program
    }
    
    while True:
        print("\n--- Expense Tracker Menu ---")
        print("1. Add Expense")  
        print("2. View Expenses (Local List View)")  
        print("3. View Expenses (Sorted by Amount)") 
        print("4. Total Spending") 
        print("5. Category Summary")  
        print("6. Delete Expenses")
        print("7. View All Master Receipts (DB View)")
        print("8. Exit")

        choice = get_menu_choice(8)
        menu_actions[choice]()

if __name__ == "__main__":
    main()