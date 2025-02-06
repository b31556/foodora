import yaml
import time




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

def read_database(table, col=False, search=False):
    if injectiondetection({"a":search,"b":col}):
        print("INJECTION DETECTED WRITING FALIED in "+search)
        return None
    try:
        conn = mysql.connector.connect(**database_config) if database_type=="mysql" else sqlite3.connect(db_name)
        cursor = conn.cursor()
        if col and search:
            cursor.execute(f"SELECT * FROM {table} WHERE {col} = {"%s" if database_type=="mysql" else "?"}", (search,))
        else:
            cursor.execute(f"SELECT * FROM {table}")

        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return None

def write_database(table="", **values: dict[str,str]):
    
    try:
        conn = mysql.connector.connect(**database_config) if database_type=="mysql" else sqlite3.connect(db_name)
        cursor = conn.cursor()
        print(f"INSERT INTO {table} ({', '.join(values.keys())}) VALUES ({', '.join(['%s' if database_type=='mysql' else '?'] * len(values))})", (tuple(values.values())))
        cursor.execute(f"INSERT INTO {table} ({', '.join(values.keys())}) VALUES ({', '.join(['%s' if database_type=='mysql' else '?'] * len(values))})", (tuple(values.values())))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def set_row(table, col, search, **values: dict[str,str]):
    
    
    try:
        conn = mysql.connector.connect(**database_config) if database_type=="mysql" else sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Generate the update query
        update_query = f"UPDATE {table} SET {', '.join([f'{key} = {"%s" if database_type=="mysql" else "?"}' for key in values.keys()])} WHERE {col} = {search}"

        # Debugging: Print the query and values
        print(update_query, tuple(values.values()))

        # Execute the update query
        cursor.execute(update_query, tuple(values.values()))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def delete_row(table, col, search):
    try:
        conn = mysql.connector.connect(**database_config) if database_type=="mysql" else sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Generate the update query
        delete_query = f"DELETE FROM {table} WHERE {col} = {"%s" if database_type=="mysql" else "?"}"

        # Debugging: Print the query and values
        print(delete_query,search)

        # Execute the update query
        cursor.execute(delete_query,(search,))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        




def setup_db(db_type, database="pincer", host=None, user=None, password=None):
    """
    Sets up the database schema for both MySQL and SQLite.
    
    :param db_type: "mysql" or "sqlite"
    :param db_name: Database name (file path for SQLite)
    :param host: MySQL host (ignored for SQLite)
    :param user: MySQL username (ignored for SQLite)
    :param password: MySQL password (ignored for SQLite)
    """
    
    # SQL Statements for Table Creation
    TABLES_L = {
        "auth": """
        CREATE TABLE IF NOT EXISTS auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            passw TEXT NOT NULL,
            createdat INTEGER NOT NULL DEFAULT 0,
            token TEXT NULL DEFAULT NULL,
            pfp TEXT NULL DEFAULT NULL,
            data TEXT NULL DEFAULT NULL CHECK (json_valid(data))
        );
        """,

        "delivery_mans": """
        CREATE TABLE IF NOT EXISTS delivery_mans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NULL DEFAULT NULL,
            email TEXT NULL DEFAULT NULL,
            pfp TEXT NULL DEFAULT NULL,
            passw TEXT NULL DEFAULT NULL,
            createdat INTEGER NULL DEFAULT NULL,
            data TEXT NULL DEFAULT NULL CHECK (json_valid(data)),
            token TEXT NULL DEFAULT NULL,
            vehicle TEXT NULL DEFAULT NULL,
            position TEXT NULL DEFAULT NULL CHECK (json_valid(position)),
            destination TEXT NULL DEFAULT NULL CHECK (json_valid(destination)),
            inprogress_order TEXT NULL DEFAULT NULL CHECK (json_valid(inprogress_order))
        );
        """,

        "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user INTEGER NULL DEFAULT NULL,
            basket TEXT NULL DEFAULT NULL CHECK (json_valid(basket)),
            restaurant TEXT NULL DEFAULT NULL,
            location TEXT NULL DEFAULT NULL CHECK (json_valid(location)),
            price INTEGER NULL DEFAULT NULL,
            status TEXT NULL DEFAULT NULL,
            createdat INTEGER NULL DEFAULT NULL,
            deliveryman_id INTEGER NULL DEFAULT NULL,
            FOREIGN KEY (user) REFERENCES auth(id) ON UPDATE NO ACTION ON DELETE NO ACTION
        );
        """
    }

    TABLES_M = {
    "auth": """
    CREATE TABLE IF NOT EXISTS auth (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        passw VARCHAR(255) NOT NULL,
        createdat INT NOT NULL DEFAULT 0,
        token TEXT NULL DEFAULT NULL,
        pfp TEXT NULL DEFAULT NULL,
        data JSON NULL DEFAULT NULL
    );
    """,

    "delivery_mans": """
    CREATE TABLE IF NOT EXISTS delivery_mans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NULL DEFAULT NULL,
        email VARCHAR(255) NULL DEFAULT NULL,
        pfp TEXT NULL DEFAULT NULL,
        passw VARCHAR(255) NULL DEFAULT NULL,
        createdat INT NULL DEFAULT NULL,
        data JSON NULL DEFAULT NULL,
        token TEXT NULL DEFAULT NULL,
        vehicle TEXT NULL DEFAULT NULL,
        position JSON NULL DEFAULT NULL,
        destination JSON NULL DEFAULT NULL,
        inprogress_order JSON NULL DEFAULT NULL
    );
    """,

    "orders": """
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user INT NULL DEFAULT NULL,
        basket JSON NULL DEFAULT NULL,
        restaurant VARCHAR(255) NULL DEFAULT NULL,
        location JSON NULL DEFAULT NULL,
        price INT NULL DEFAULT NULL,
        status VARCHAR(255) NULL DEFAULT NULL,
        createdat INT NULL DEFAULT NULL,
        deliveryman_id INT NULL DEFAULT NULL,
        FOREIGN KEY (user) REFERENCES auth(id) ON UPDATE NO ACTION ON DELETE NO ACTION
    );
    """
}


    try:
        if db_type == "sqlite":
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            TABLES=TABLES_L
        elif db_type == "mysql":
            conn = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            cursor = conn.cursor()
            # Adjusting tables for MySQL (replacing SQLite-specific parts)
            TABLES=TABLES_M

        else:
            raise ValueError("Unsupported database type. Use 'mysql' or 'sqlite'.")

        # Create tables if they don't exist
        for table_name, table_sql in TABLES.items():
            cursor.execute(table_sql)

        conn.commit()
        print(f"✅ Database setup completed successfully for {db_type}!")

    except Exception as e:
        print(f"❌ Error setting up database: {e}")

    finally:
        cursor.close()
        conn.close()






with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)
    
database_type=conf["database_infos"]["type"]

if database_type=='mysql':
    import mysql.connector
    config=conf["database_infos"]
    database_config = {
    'user': config["user"],        
    'password': config["password"],  
    'host': config["host"],     
    'database': config["database"]  
    }
else:
    import sqlite3
    database_type="sqlite"
    db_name=f"data/{conf["database_infos"]["database"] if conf["database_infos"]["database"]!="" else "database"}.db"
    database_config={'database':db_name}

setup_db(db_type=database_type,**database_config)

