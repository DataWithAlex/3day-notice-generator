import streamlit as st
import pandas as pd
from fillpdf import fillpdfs
from pdfrw import PdfReader, PdfWriter, PageMerge
import os
import tempfile
import zipfile

# Function to generate individual 3-day notices
def generate_notices(csv_file, due_date, month, year, mailed_date):
    # Read CSV file
    df = pd.read_csv(csv_file)

    # Filter necessary columns
    df = df[['tenant', 'full_adress', 'address_1', 'address_2', 'money', 'county', 'zip']]

    # List to keep track of generated PDFs
    generated_files = []

    for index, row in df.iterrows():
        # Prepare data for each tenant
        data_dict = {
            'tenant': row['tenant'],
            'address_1': row['address_1'],
            'address_2': row['address_2'],
            'money': row['money'],
            'county': row['county'],
            'due_date': due_date,
            'month': month,
            'year': year,
            'mailed_date': mailed_date,
            'company_2': 'The Experts Team Realty, Inc',
            'phone': '407-674-7994',
            'date_1': mailed_date,
            'date_2': mailed_date,
            'company': 'The Experts Team Realty, Inc',
            'full_adress': row['full_adress']
        }

        # Create a unique PDF name for each notice
        pdf_name = f"{index}_{row['address_1'].replace(' ', '_')}_3day.pdf"

        # Fill PDF form fields with data and save the file
        fillpdfs.write_fillable_pdf('temp.pdf', pdf_name, data_dict)

        # Flatten the filled PDF to avoid black box issues
        flatten_pdf(pdf_name)

        # Store the generated file path for zipping
        generated_files.append(pdf_name)

    return generated_files

# Function to flatten a PDF using pdfrw to avoid black boxes
def flatten_pdf(input_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Merge page content to flatten form fields
        PageMerge(page).render()

        writer.addpage(page)

    with open(input_pdf_path, 'wb') as out_file:
        writer.write(out_file)

# Function to create a ZIP file of all generated PDFs
def create_zip_file(pdf_files):
    # Create a temporary file for the ZIP
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        with zipfile.ZipFile(tmp_zip.name, 'w') as zipf:
            for pdf_file in pdf_files:
                zipf.write(pdf_file, os.path.basename(pdf_file))
        return tmp_zip.name

# Streamlit app interface
st.title("3-Day Notice Generator")

# File uploader
csv_file = st.file_uploader("Upload CSV file", type=["csv"])

# User inputs for dates
due_date = st.text_input("Enter Due Date (e.g., 19th)")
month = st.text_input("Enter Month (e.g., August)")
year = st.text_input("Enter Year (e.g., 24)")
mailed_date = st.text_input("Enter Mailed Date (e.g., 08/02/2024)")

if st.button("Generate 3-Day Notices"):
    if csv_file and due_date and month and year and mailed_date:
        generated_files = generate_notices(csv_file, due_date, month, year, mailed_date)

        st.success(f"3-Day Notices generated for {len(generated_files)} properties.")

        # Create a zip file of all PDFs
        zip_file_path = create_zip_file(generated_files)

        # Provide a download link for the ZIP file
        with open(zip_file_path, "rb") as zip_file:
            st.download_button(
                label="Download All Notices as ZIP",
                data=zip_file.read(),
                file_name="3day_notices.zip"
            )

        # Clean up the generated files after download
        for file_path in generated_files:
            os.remove(file_path)
        os.remove(zip_file_path)

    else:
        st.error("Please provide all necessary inputs!")
