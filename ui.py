import os
import streamlit as st
import requests
from dotenv import load_dotenv
import sqlite3
import csv


css = """
<style>
.i-button-container {
    display: flex;
    align-items: center;
}
.i-button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 20px;
    margin-left: 5px;
}
.i-description {
    display: none;
    padding: 10px;
    background-color: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 5px;
}
.i-button-container:hover .i-description {
    display: block;
}
</style>
"""

# Add the custom CSS to the Streamlit app
st.markdown(css, unsafe_allow_html=True)

# Load environment variables
load_dotenv()
api_host = os.environ.get("HOST", "0.0.0.0")
api_port = int(os.environ.get("PORT", 8080))

sql_db_path = os.environ.get("SQL_DATABASE_FILE_PATH","")

# Streamlit UI elements
st.title("AI-CSV Sage : AI-Enabled CSV Reports")

description_expander = st.expander("About", expanded=False)
description_expander.write("AI-CSV Sage is a powerful tool designed to streamline and simplify the process of generating CSV reports from large databases using the capabilities of artificial intelligence (AI). With AI-CSV Sage, users can provide a brief description of the specific reports they require, including details about the data elements, criteria, and any specific information of interest. The tool leverages AI and large language models to intelligently interpret and execute these requests, tailoring the reports to meet the user's needs.""\n\nPlease note: AI-CSV Sage is currently developed specifically for SQLite3 databases.")

# Show or hide the description when the "i" button is clicked
description_expander.expanded = not description_expander.expanded


question = st.text_input(
    "Please provide a brief description of the report you'd like to generate.",
    placeholder="What data are looking for?"
)

# Define the description as an expander

if question:
    url = f'http://{api_host}:{api_port}/'
    data = {"query": question}

    if  sql_db_path:
        response = requests.post(url, json=data)
        f=open('/home/noorlearning/Downloads/response.txt','a')

        if response.status_code == 200:
            st.write("### Answer")
            # st.write(response.json())
            final_response=str(response.json())
            try:
                db_connection = sqlite3.connect(sql_db_path)  
                cursor = db_connection.cursor()

                # Execute SQL commands
                cursor.execute(final_response)
                data = cursor.fetchall()
                f.write('\nDatabase  :\n' + str(data)+"---> \nData Type : "+ str(type(data)))
                with open('reports/report.csv', 'w', newline='') as file:
                    csv_writer = csv.writer(file)
                    
                    # Write the header
                    header = [description[0] for description in cursor.description]
                    csv_writer.writerow(header)
                    
                    # Write the data rows
                    csv_writer.writerows(data)
                st.write('Your file generated. Download it from here ')
                
                f.close()
                download_button = st.download_button(
                    label="Download CSV",
                    data=open('reports/report.csv', 'rb').read(),
                    key='download_button',
                    on_click=None,
                    file_name='generated_report.csv'  # Specify the file name and extension
                )
            except Exception as e:
                st.error(f'We can not generate a Excel file for your request. Please change or modify the question.\n Error : {e}')

        else:
            st.error(f"Failed to send data to Pathway API. Status code: {response.status_code}")
    else:
                # st.write('### Alert')
        st.error(f'Please add Your Sql Database path in env file {sql_db_path}')
