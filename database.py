import mysql.connector
import time

database_config = {
    'user': 'pincer',        # Replace with your MariaDB username
    'password': 'authinside?',  # Replace with your MariaDB password
    'host': 'localhost',         # Replace with your MariaDB host
    'database': 'pincer'  # Replace with your database name
}



# RAW functions

def injectiondetection(ob):
    danger=["\"","\'",")","("]
    for o in ob.keys():
        for dang in danger:
            if dang in o:
                return True
    for o in ob.values():
        try:
            for dang in danger:
                if dang in o:
                    return True
        except:
            pass
    return False

def read_database(table, col, search):
    if injectiondetection({"a":search,"b":col}):
        print("INJECTION DETECTED WRITING FALIED in "+search)
        return None
    try:
        conn = mysql.connector.connect(**database_config)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE {col} = %s", (search,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return None

def write_database(table="", **values: dict[str,str]):
    
    try:
        conn = mysql.connector.connect(**database_config)
        cursor = conn.cursor()
        print(f"INSERT INTO {table} ({', '.join(values.keys())}) VALUES ({', '.join(['%s'] * len(values))})", (tuple(values.values())))
        cursor.execute(f"INSERT INTO {table} ({', '.join(values.keys())}) VALUES ({', '.join(['%s'] * len(values))})", (tuple(values.values())))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def set_row(table, col, search, **values: dict[str,str]):
    
    
    try:
        conn = mysql.connector.connect(**database_config)
        cursor = conn.cursor()

        # Generate the update query
        update_query = f"UPDATE {table} SET {', '.join([f'{key} = %s' for key in values.keys()])} WHERE {col} = {search}"

        # Debugging: Print the query and values
        print(update_query, tuple(values.values()))

        # Execute the update query
        cursor.execute(update_query, tuple(values.values()))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
