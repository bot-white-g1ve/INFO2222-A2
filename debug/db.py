import sqlite3

def show_all_table(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    conn.close()

def print_table(cursor, table_name):
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

def delete_table(cursor, table_name):
    # 测试表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if cursor.fetchone() is None:
        print(f"Table '{table_name}' does not exist.")
    else:
        # 删除表中的所有数据
        cursor.execute(f"DELETE FROM {table_name};")
        conn.commit()  # 确保提交更改
        print(f"All data from '{table_name}' has been deleted.")

def add_column(cursor, table_name, column_name):
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT;")
        print(f"Column '{column_name}' added to table '{table_name}' successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error adding column: {e}")
    
    
if __name__ == '__main__':
    db_file = "database/main.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    #show_all_table(db_file)
    #print_table(cursor, "user")
    delete_table(cursor, "user")
    #add_column(cursor, "user", "priKey")
    conn.commit()
    conn.close()
