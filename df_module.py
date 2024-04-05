import pandas as pd
import mysql.connector
import streamlit as st



def table_exists(cursor, database_name, table_name):
    cursor.execute(f"SHOW TABLES FROM {database_name} LIKE '{table_name}'")
    return cursor.fetchone() is not None


def create_connection():
    try:
        cols = st.columns(5)
        host = cols[0].text_input("hostname", value='localhost', key='lhost')
        user = cols[1].text_input("username", value='root', key='uer')
        password = cols[2].text_input("Password", value='Vikas@123', key='passwd')
        db = cols[3].text_input("database", value='business_card_unstructured', key='db')
        table_name = cols[4].text_input("table name", value='text_extract', key='table_name')  
        return host, user, password, db, table_name
    except Exception as e:
        st.error(f"Error in creating connection to MySQL Server: {str(e)}")
        return None, None, None, None, None 


def connect_to_mysql(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conn
    except Exception as e:
        st.error(f"Error in establishing connection to MySQL Server: {str(e)}")
        return None




def create_table(conn, df, table_name):
    try:
        cursor = conn.cursor()
        columns = []

        # Check if the table exists
        existing_tables_query = f"SHOW TABLES LIKE '{table_name}'"
        cursor.execute(existing_tables_query)
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            for col, dtype in df.dtypes.items():
                if pd.api.types.is_string_dtype(dtype):
                    sql_type = "VARCHAR(255)"
                elif pd.api.types.is_integer_dtype(dtype):
                    sql_type = "BIGINT"
                elif pd.api.types.is_float_dtype(dtype):
                    sql_type = "FLOAT"
                elif pd.api.types.is_bool_dtype(dtype):
                    sql_type = "BOOLEAN"
                else:
                    sql_type = "VARCHAR(255)"

                columns.append(f"{col} {sql_type}")

            columns_str = ", ".join(columns)
            create_table_query = f"CREATE TABLE {table_name} ({columns_str})"
            cursor.execute(create_table_query)
        cursor.close()
    except Exception as e:
        st.write(f"Error creating table: {str(e)}")




def insert_data(conn, df, table_name, append=False):
    try:
        cursor = conn.cursor()
        
        if append:
            # If append mode is enabled, simply insert data into the table
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            data = [tuple(row) for row in df.values]
            cursor.executemany(query, data)
            conn.commit()
        else:
            # Otherwise, check if the table exists and create it if needed
            existing_tables_query = f"SHOW TABLES LIKE '{table_name}'"
            cursor.execute(existing_tables_query)
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                # If the table does not exist, create it
                columns = []
                for col, dtype in df.dtypes.items():
                    if pd.api.types.is_string_dtype(dtype):
                        sql_type = "VARCHAR(255)"
                    elif pd.api.types.is_integer_dtype(dtype):
                        sql_type = "BIGINT"
                    elif pd.api.types.is_float_dtype(dtype):
                        sql_type = "FLOAT"
                    elif pd.api.types.is_bool_dtype(dtype):
                        sql_type = "BOOLEAN"
                    else:
                        sql_type = "VARCHAR(255)"

                    columns.append(f"{col} {sql_type}")

                columns_str = ", ".join(columns)
                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
                cursor.execute(create_table_query)

                # Insert data into the newly created table
                columns = ', '.join(df.columns)
                placeholders = ', '.join(['%s'] * len(df.columns))
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                data = [tuple(row) for row in df.values]
                cursor.executemany(query, data)
                conn.commit()

        cursor.close()
    except Exception as e:
        st.write(f"Error inserting into table: {str(e)}")
        st.warning("Try entering a different table name!")

                
