import streamlit as st
import numpy as np
import pandas as pd
import easyocr
import io
import os
import mysql.connector 
from df_module import *
#from google.cloud import vision
#from google.cloud.vision_v1 import types
# import altair as alt


def header():
  # Page title
  st.set_page_config(page_title='BizCard Reader', page_icon='📷➡️📝')
  st.title('📷➡️📝 BizCard Reader')

  with st.expander('About this app'):
    st.markdown('**What can this app do?**')
    st.info('Can extract a business card image into text data. The text data is displayed as table with relevant headers.')
    st.markdown('**How to use the app?**')
    st.warning('Select appropriate options below, 1. Click on the upload button to load the image, and then  2. Select the view option to see the data as table. One can also parse the previously fetched results.')
    
  st.subheader('Read carefully the headers!')




@st.cache_data
def extractor(image_bytes):
    # Create an OCR reader
    reader = easyocr.Reader(['en'])
    res = reader.readtext(image_bytes)
    return [detection[1] for detection in res]


# def organize_text(res):
#   try:
#     # for ls in res:
#     #   st.write(ls)
#     # Convert the list of strings into a single string separated by newlines
#     text_content = "\n".join(res)
#     custom_css = '''
#         <style>
#             div.css-1om1ktf.e1y61itm0 {
#               width: 800px;
#             }
#         </style>
#         '''
#     st.markdown(custom_css, unsafe_allow_html=True)
#     #user_input = st.text_area("Type your text here:", height=400)
#     # Display the text area in Streamlit app

#     # Create a text input field for each line in text_content
#     for i, line in enumerate(res):
#         user_input = st.text_input(f"Line {i+1}", value=line)

#     # Arrange button to display the edited list
#     if st.button("Submit"):
#         # Get the edited content from the text input fields
#         edited_content = [st.text_input(f"Line {i+1}", value=line) for i, line in enumerate(res)]
#         st.text("Edited Content:")
#         st.write(edited_content)  
        
#     #user_input = st.text_area("Text extracted", value=text_content, height=300)
#     return user_input  
#   except Exception as e:
#     st.write("Error:", e)
#     return None  


# # Define function to perform OCR on image
# def perform_ocr(image):
#     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vision_api.json"
#     client = vision.ImageAnnotatorClient()
#     with st.spinner('Performing OCR...'):
#         content = image.read()
#         image = types.Image(content=content)
#         response = client.text_detection(image=image)
#         texts = response.text_annotations
#         return texts

     
def streamlit_uploader():
    st.markdown('<span style="color: green;">STEP 1: Upload image(s)</span>', unsafe_allow_html=True)      
    uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files is not None:
        if len(uploaded_files) == 1:
            uploaded_file = uploaded_files[0]
            uploaded_image = st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
            st.markdown('<span style="color: green;">STEP 2: Extract text from Image.</span>', unsafe_allow_html=True)               
            
            cols = st.columns(5)
            extract_button = cols[2].button('Extract Text', key='exttract text data')
            if not st.session_state.get('extractButton'):
                st.session_state['extractButton'] = extract_button
                    
            if st.session_state['extractButton']:
                image_bytes = uploaded_file.read()
                res = extractor(image_bytes) 
                if res is not None:
                    uploaded_image.empty()
                    
                    
                    st.markdown('<span style="color: green;">STEP 3: Arrange right column according to left.</span>', unsafe_allow_html=True)               

                    
                    
                    # Initialize session state to store user inputs
                    user_inputs = res
                    
                    # Create two columns for text input fields
                    col1, col2 = st.columns(2)
    
                    # Loop through the lines and create text input fields in each column
                    for i, line in enumerate(user_inputs):
                        #st.write(line)
                        with col2:
                            user_input = st.text_input(f"Line {i+1}", value=line, key=f"user_input_{i}")
                            user_inputs[i] = user_input
    
                    col_name = ["name", "designation", "phone_number", "email", "website", "company", "address"]
                    for i in range(7):            
                        with col1:
                            #st.markdown(f'<div style="color: blue;">{line}</div>', unsafe_allow_html=True)
                            st.text_input(f"Line {i+1}", value=col_name[i], key=f"user_input1_{i}", disabled=True)
                            
                            #st.text_input(f"Line {i+1}", value=col_name[i], key=f"user1_input_{i}")
                            #st.session_state.user_inputs[i] = user_input
                    
                    employee_data = [[user_inputs[i] for i in range(7)]]                    
                    df = pd.DataFrame(employee_data, columns=col_name)


                    st.markdown('<span style="color: green;">STEP 4: Fill in server and databse details below.</span>', unsafe_allow_html=True)               

                    
                    col = st.columns(5)
                    upload_button = col[2].button('Upload', key='trying to upload to mysql')
                    if not st.session_state.get('uploadButton'):
                        st.session_state['uploadButton'] = upload_button
                            
                    if st.session_state['uploadButton']:  
                        if not bool(user_inputs[8]):

                            st.dataframe(df)   

                             
                            host, user, password, db, table_name = create_connection() 
                            conn = connect_to_mysql(host, user, password, db)
                            col1 = st.columns(5)
                            insert_button = col1[2].button('Click to upload', key='upload to mysql')                            
                            if insert_button:
                                insert_data(conn, df, table_name, True)
                                st.success("Uploaded to MySQL local server successfully!")
                                st.session_state['extractButton'] = False
                                st.session_state['uploadButton'] = False

                        else:
                            st.warning("Oops: You have not set the left column in accordance with the right column!")
                            st.warning("To upload, this step is mandatory.")
    
                else:
                    uploaded_image.empty()
                    st.error("No text found!")
        else:
            st.markdown("STEP 3: To upload data in MySQL, make sure left column aligns with the right!") 
            cols = st.columns(5)
            extract_button = cols[2].button('Extract Text', key='exttract text data')
            if not st.session_state.get('extractButton'):
                st.session_state['extractButton'] = extract_button
                    
            if st.session_state['extractButton']:
                # Convert the file to bytes
                
                image_bytes = [uploaded_file.read() for uploaded_file in uploaded_files]
                #proces = st.spinner("Processing...")
                res = [" ".join(extractor(image_byte)) for image_byte in image_bytes]  
                df = pd.DataFrame(res, columns=['Text_extracted'])
                if res:
                    st.dataframe(df) 
                    col = st.columns(3)
                    upload_button = col[1].button('Upload to MySQL', key='upload to mysql1')  

                    if not st.session_state.get('uploadButton'):
                        st.session_state['uploadButton'] = upload_button
                            
                    if st.session_state['uploadButton']:
                      
                        host, user, password, db, table_name = create_connection() 
                        conn = connect_to_mysql(host, user, password, db)

                        col1 = st.columns(5)
                        upload = col1[2].button('Click to upload', key='upload to mysql2')  
                        if not st.session_state.get('uploadButton1'):
                            st.session_state['uploadButton1'] = upload
                                
                        if st.session_state['uploadButton1']:   
                            create_table(conn, df, table_name)                           

                            insert_data(conn, df, table_name, True)
                            st.success("Uploaded to MySQL local server successfully!")
                            st.session_state['extractButton'] = False
                            st.session_state['uploadButton'] = False

        


   
                        
# def create_table(conn, df, table_name):

#     # cursor = conn.cursor()
#     # columns = []

#     # for col, dtype in df.dtypes.items():
#     #     if pd.api.types.is_string_dtype(dtype):
#     #         sql_type = "VARCHAR(255)"
#     #     elif pd.api.types.is_integer_dtype(dtype):
#     #         sql_type = "BIGINT"
#     #     elif pd.api.types.is_float_dtype(dtype):
#     #         sql_type = "FLOAT"
#     #     elif pd.api.types.is_bool_dtype(dtype):
#     #         sql_type = "BOOLEAN"
#     #     else:
#     #         sql_type = "VARCHAR(255)"

#     #     columns.append(f"{col} {sql_type}")

#     # columns_str = ", ".join(columns)
#     # create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
#     # cursor.execute(create_table_query)
#     # cursor.close()
#     try:
#         cursor = conn.cursor()
#         columns = []

#         # Check if the table exists
#         existing_tables_query = f"SHOW TABLES LIKE '{table_name}'"
#         cursor.execute(existing_tables_query)
#         table_exists = cursor.fetchone() is not None

#         if not table_exists:
#             for col, dtype in df.dtypes.items():
#                 if pd.api.types.is_string_dtype(dtype):
#                     sql_type = "VARCHAR(255)"
#                 elif pd.api.types.is_integer_dtype(dtype):
#                     sql_type = "BIGINT"
#                 elif pd.api.types.is_float_dtype(dtype):
#                     sql_type = "FLOAT"
#                 elif pd.api.types.is_bool_dtype(dtype):
#                     sql_type = "BOOLEAN"
#                 else:
#                     sql_type = "VARCHAR(255)"

#                 columns.append(f"{col} {sql_type}")

#             columns_str = ", ".join(columns)
#             create_table_query = f"CREATE TABLE {table_name} ({columns_str})"
#             cursor.execute(create_table_query)
#         cursor.close()
#     except Exception as e:
#         st.write(f"Error creating table: {str(e)}")

                    


# def table_exists(cursor, table_name):
#     # Query to check if the table exists
#     try:
#         cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
#         return cursor.fetchone() is not None
#     except Exception as e:
#         st.error(f"Error creating table: {str(e)}") 
#         return False


# def create_employee_table(database, create_table_query):
#     try:
#         cols = st.columns(5)
#         host = cols[1].text_input("hostname", value='localhost', key='lhost')
#         user = cols[2].text_input("username", value='root', key='uer')
#         password = cols[3].text_input("Password", value='Vikas@123', key='passwd')

#         #database = 'business_card'
        
#         # Connect to MySQL server
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password
#         )
    
#         # Create a cursor object
#         cursor = connection.cursor()
    
#         # Define the SQL query to create the database if it doesn't exist
#         create_database_query = f"CREATE DATABASE IF NOT EXISTS {database}"
        
#         # Execute the SQL query to create the database
#         cursor.execute(create_database_query) 
    
#         connection.commit()
    
#         # Close cursor and connection
#         cursor.close()
#         connection.close()
    
    
    
    
    
    
    
    
#         # Connect to MySQL server
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )
    
#         # Create a cursor object
#         cursor = connection.cursor()
    
       
    
#         # # Check if the table already exists
#         # if table_exists(cursor, table_name):
#         #     st.success(f"Uploading to '{table_name}' table! It already exists!")
#         # else:
#         #     st.warning(f"Table '{table_name}' does not exists! Created one!")
    
    

    
#         # Execute the SQL query to create the table
#         cursor.execute(create_table_query)
    
#         # Commit changes to the database
#         connection.commit()
    
#         # Close cursor and connection
#         cursor.close()
#         connection.close()

#         return host, user, password
#     except Exception as e:
#         st.error(f"Error creating table: {str(e)}")
#         return None, None, None  


# def insert_employee_data(host, user, password, database, insert_query, data):
#     # Connect to MySQL server
#     if host:
#       try:
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )

#         # Create a cursor object
#         cursor = connection.cursor()


#         # Execute the SQL query to insert data into the table
#         cursor.executemany(insert_query, data)

#         # Commit changes to the database
#         connection.commit()

#         # Close cursor and connection
#         cursor.close()
#         connection.close()
#       except Exception as e:
#           st.write(f"Error creating table: {str(e)}")



def main():
  header()
  streamlit_uploader()
  
  #insert_employee_data(host, user, password, 'business_card', res)

if __name__ == "__main__":
    main()
