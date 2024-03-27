import sqlite3

def print_all_table(db_file):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    conn.close()

def print_table(db_file, table_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #test if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if cursor.fetchone() is None:
        print(f"Table '{table_name}' does not exist.")
        conn.close()
        return  
    
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == '__main__':
    db_file = "database/main.db"
    #print_all_table(db_file)
    print_table(db_file, "user")
