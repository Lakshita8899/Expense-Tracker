 


#sort the expenses in desecnding order.
#TODO
#error handling
#extend this application to multiple users
#integrate logging
#integrate with sql lite
#separate table for user and have foreign key constraints
#include delete and edit option
import json 
import datetime
import sqlite3
expenses = []
current_user=""
current_user_id = None
def init_db():
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute(""" 
    create table if not exists users(
    id integer primary key Autoincrement,
    username TEXT unique not null);
    """)
    cursor.execute("""
    create table if not exists expenses( 
    id integer primary key autoincrement,
    amount REAL NOT NULL,
    category TEXT not null,
    description TEXT,
    user_id INTEGER,
    foreign key (user_id) REFERENCES user(id));
    """)
    
 
def log_activity(action):
        timestamp= datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line= f"[{timestamp}] {action}\n" 
        with open("activity_log.txt","a") as file:
            file.write(log_line)
         
def login_user():
    global current_user, current_user_id
    name = input("Enter your username to login: ").strip().lower()
    
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute("insert or ignore into users (username) values (?);", (name,))
    conn.commit()
    
 
    cursor.execute("select id from users where username = ?;", (name,))
    result = cursor.fetchone()
    current_user = name
    current_user_id = result[0]
    
    print(f"Welcome, {current_user.capitalize()}! Your Database ID is: {current_user_id}")
    conn.close()
def load_expenses():
    global expenses
    box_name=f"{current_user}_expenses.json"
    try:
        with open(box_name,"r") as file:
            expenses=json.load(file)
            print("your past data is loaded succesfully")
    except FileNotFoundError:
        print("No previous history found")
 
def save_expenses():
    box_name = f"{current_user}_expenses.json"
    with open(box_name,"w") as file:
        json.dump(expenses,file)
        print("progress saves permanently to your personal file")
def get_valid_amount():
    while True:
        try:
            amt = float(input("enter the amount: "))
            if amt >=0:
                return amt   
            else:
                print(f"{amt} is invalid")
        except ValueError:
            print("Invalid number. Please enter digits only.")  
def delete_expenses():
    global expenses
    conn=sqlite3.connect("tracker.db")
    cursor = conn.cursor()

    cursor.execute("select id , amount, category from expenses where  user_id = ?;",( receipt_id,current_user_id,))
    rows = cursor.fetchall()
    print("your active receipt")
    for row in row:
        print(f"recipt id :{row[0]} | Amount: {row[1]} | Category: {row[2]}")

        receipt_id=int(input("enter your id to delete"))

        cursor.execute("delete from expenses where id = ? AND receipt_id=?;",(receipt_id,))
        conn.commit()
        conn.close()
        print(f"Receipt #{receipt_id} deleted successfully from database grid!")


def get_menu_choice():
    while True:
        choice = input("Enter your choice (1-6): ")
        if choice in ["1", "2", "3", "4", "5","6"]:
            return choice   
        else:
            print("Invalid choice, try again!")

def add_expenses():
    amt = get_valid_amount()
    
    cat = input("select category(food ,travel ,etc):")
    des = input("description :")
    conn = sqlite3.connect("tracker.db")
    cursor = conn.cursor()
    cursor.execute("""insert into expenses (amount,category,description,user_id) values (?,?,?,?);""",(amt,cat,des,current_user_id))
    conn.commit()
    conn.close()

    print("expenses logges safely in database grid")

    new_expenses = {
        "amount" : amt , 
        "category" : cat ,
        "description" : des
    }
 

    print("expenses added")
    expenses.append(new_expenses)
    save_expenses()
    log_activity(f"EXPENSE: User '{current_user}' added {amt} in '{cat}'.")
  
def view_expenses():
    for items in expenses :
        print(items["amount"], items["category"], items["description"])
      
def view_sorted_expenses():
    if not expenses:
        print("your tracker is empty.")
        return 
    
    print("how would you like to sort?")
    print("1.ascending order")
    print("2.descending order")
    order = input("enter choice (1-2):")

    if order == "1":
        expenses.sort(key=lambda item: item["amount"])
        print("Expenses (Lowest to Highest)")
    elif order == "2":
        expenses.sort(key = lambda items :items["amount"] ,reverse = True)
        print("Expenses (Highest to Lowest)")
    else:
        print("Invalid choice. Showing unsorted data")
    for items in expenses:
        print(items["amount"], items["category"], items["description"])
def total_spending():
    total=0
    for items in expenses:
        total = total + items["amount"]
    print(total)


def category_summary():
    summary = {}
    for items in expenses:
        cat = items["category"]
        amt = items["amount"]
        if cat in summary:
            summary[cat] = summary[cat] + amt
        else:
            summary[cat] = amt
    for cat, total in summary.items():
        print(f"{cat}: {total}")
 

def main():
    init_db()
    print("Welcome To Intel Tracker")
   
    login_user()
    load_expenses()
    while True :
        print("\n--- Expense Tracker Menu ---")
        print("1. Add Expense")  
        print("2. View Expenses")  
        print("3.View Expenses (Sorted by Amount)") 
        print("4. Total Spending") 
        print("5. Category Summary")  
        print("6. Exit")

        choice = get_menu_choice()

        if choice == "1":
            add_expenses()
        elif choice =="2":
            view_expenses()
        elif choice == "3":
            view_sorted_expenses()
        elif choice == "4":
            total_spending()
        elif choice == "5":
            category_summary()
        elif choice == "6":
            print("Goodbye!")
            break
         
        
      
if __name__ == "__main__":
    main()

 