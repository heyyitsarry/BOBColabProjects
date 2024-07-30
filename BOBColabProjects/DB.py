import pyodbc
import pandas as pd

# Database connection details
server = 'your_server_name'
database = 'StoStatDataBase'
username = 'your_username'
password = 'your_password'

# Create a database connection
def get_connection():
    conn_str = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password}'
    )
    return pyodbc.connect(conn_str)

# Execute a SQL query
def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    cursor.close()
    conn.close()

# Retrieve data from a table
def fetch_data(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Insert data into CurrencyChests table
def add_currency_chest(location, currency_type, amount):
    query = "INSERT INTO CurrencyChests (ChestLocation, CurrencyType, Amount, LastUpdated) VALUES (?, ?, ?, GETDATE())"
    execute_query(query, (location, currency_type, amount))

# Update currency chest amount
def update_currency_chest(chest_id, amount):
    query = "UPDATE CurrencyChests SET Amount = ?, LastUpdated = GETDATE() WHERE ChestID = ?"
    execute_query(query, (amount, chest_id))

# Delete a currency chest
def delete_currency_chest(chest_id):
    query = "DELETE FROM CurrencyChests WHERE ChestID = ?"
    execute_query(query, (chest_id,))
