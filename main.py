
import sqlite3
from datetime import date

DB_NAME = "expense_tracker.db"



def initialize_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS transactions (
                                                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                 type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                         category TEXT NOT NULL,
                         amount REAL NOT NULL CHECK (amount > 0),
                         transaction_date TEXT NOT NULL
                         )
                     """)



def get_amount():
    while True:
        try:
            amount = float(input("Enter amount: "))

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            return round(amount, 2)

        except ValueError:
            print("Enter a valid number, for example 25.50.")



def add_transaction(transaction_type):
    print(f"\n--- Add {transaction_type.title()} ---")

    category = input("Enter category: ").strip()

    if not category:
        print("Category cannot be empty.")
        return

    amount = get_amount()
    transaction_date = input(
        "Enter date (YYYY-MM-DD) or press Enter for today: "
    ).strip()

    if not transaction_date:
        transaction_date = str(date.today())
    else:
        try:
            transaction_date = str(
                date.fromisoformat(transaction_date)
            )
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")
            return

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
                     INSERT INTO transactions
                         (type, category, amount, transaction_date)
                     VALUES (?, ?, ?, ?)
                     """, (transaction_type, category, amount, transaction_date))

    print(f"{transaction_type.title()} saved successfully!")



def view_transactions():
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
                            SELECT id, transaction_date, type, category, amount
                            FROM transactions
                            ORDER BY transaction_date DESC, id DESC
                            """).fetchall()

    print("\n--- Transaction History ---")

    if not rows:
        print("No transactions recorded yet.")
        return

    for row in rows:
        transaction_id, trans_date, trans_type, category, amount = row

        print(
            f"ID: {transaction_id} | {trans_date} | "
            f"{trans_type.title()} | {category} | {amount:.2f}"
        )



def show_summary():
    with sqlite3.connect(DB_NAME) as conn:
        income, expenses = conn.execute("""
                                        SELECT
                                            COALESCE(SUM(CASE WHEN type = 'income'
                                                                  THEN amount ELSE 0 END), 0),
                                            COALESCE(SUM(CASE WHEN type = 'expense'
                                                                  THEN amount ELSE 0 END), 0)
                                        FROM transactions
                                        """).fetchone()

    print("\n--- Financial Summary ---")
    print(f"Total income:   {income:.2f}")
    print(f"Total expenses: {expenses:.2f}")
    print(f"Balance:        {income - expenses:.2f}")

def delete_transaction():
    view_transactions()

    try:
        transaction_id = int(
            input("\nEnter the ID of the transaction to delete: ")
        )
    except ValueError:
        print("Please enter a valid numeric ID.")
        return

    confirm = input(
        f"Are you sure you want to delete transaction "
        f"{transaction_id}? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Deletion cancelled.")
        return

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

        if cursor.rowcount == 0:
            print("No transaction found with that ID.")
        else:
            print("Transaction deleted successfully!")

def view_monthly_transactions():
    month = input(
        "Enter month (YYYY-MM), for example 2026-10: "
    ).strip()

    try:
        date.fromisoformat(month + "-01")
    except ValueError:
        print("Invalid month. Use YYYY-MM, for example 2026-10.")
        return

    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
                            SELECT id, transaction_date, type, category, amount
                            FROM transactions
                            WHERE transaction_date LIKE ?
                            ORDER BY transaction_date DESC, id DESC
                            """, (month + "-%",)).fetchall()

    print(f"\n--- Transactions for {month} ---")

    if not rows:
        print("No transactions found for this month.")
        return

    for row in rows:
        transaction_id, trans_date, trans_type, category, amount = row
        print(
            f"ID: {transaction_id} | {trans_date} | "
            f"{trans_type.title()} | {category} | {amount:.2f}"
        )





def main():
    initialize_db()

    while True:
        print("\n===== PERSONAL EXPENSE TRACKER =====")
        print("1. Add income")
        print("2. Add expense")
        print("3. View transactions")
        print("4. View financial summary")
        print("5. Delete transaction")
        print("6. View transactions by month")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_transaction("income")
        elif choice == "2":
            add_transaction("expense")
        elif choice == "3":
            view_transactions()
        elif choice == "4":
            show_summary()
        elif choice == "5":
            delete_transaction()
        elif choice =="6" :
            view_monthly_transactions()
        elif choice =="7":
            print("Thank you for using Expense Tracker!")
            break
        else:
            print("Invalid choice. Choose from 1-7.")


if __name__ == "__main__":
    main()
