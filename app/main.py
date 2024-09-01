import streamlit as st
import pandas as pd
import zipfile
import os
import logging
import matplotlib.pyplot as plt
from apple_health_exporter import AppleHealthExporter 

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - Line %(lineno)d - %(message)s')

# Function to extract ZIP file
def extract_zip(uploaded_file):
    logging.info("Starting extraction of ZIP file.")
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall("temp_data/")
        export_file = os.path.join("temp_data/apple_health_export/", 'export.xml')
        logging.info(f"Looking for export.xml at {export_file}.")
        if os.path.exists(export_file):
            logging.info("export.xml found.")
            return export_file
    logging.warning("export.xml not found in the ZIP file.")
    return None

# Function to convert XML to CSV
def convert_xml_to_csv(xml_file_path, csv_output_dir, include_tags):
    try:
        logging.info(f"Converting XML file {xml_file_path} to CSV.")
        converter = AppleHealthExporter(xml_file_path, csv_output_dir, include_tags)
        converter.convert()
        logging.info("Conversion successful.")
        return os.listdir(csv_output_dir)
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return []

# Function to preprocess the data
def preprocess_data(files):
    logging.info("Starting data preprocessing.")
    combined_data = pd.DataFrame()
    for file in files:
        logging.info(f"Reading file: {file}")
        data = pd.read_csv(f"data/apple_health_export/csv_output/{file}")
        combined_data = pd.concat([combined_data, data], ignore_index=True)  
    logging.info("Data preprocessing completed.")
    return combined_data

# Function to visualize data
def visualize_data(data):
    st.subheader("Data Overview")
    st.write(data.head())  # Show first few rows of data

    # Example visualization: Histogram of a column (modify this based on your data)
    if 'steps' in data.columns:
        plt.figure(figsize=(10, 5))
        plt.hist(data['steps'], bins=20, color='skyblue', edgecolor='black')
        plt.title('Distribution of Steps')
        plt.xlabel('Steps')
        plt.ylabel('Frequency')
        st.pyplot(plt)

# Main Streamlit app
def main():
    st.title('Vitalis: Apple Health Data Analyzer')

    uploaded_file = st.file_uploader("Upload a ZIP file", type=["zip"])

    if uploaded_file is not None:
        logging.info("A file has been uploaded.")
        st.write("Extracting data...")
        xml_file = extract_zip(uploaded_file)

        if xml_file:
            st.write("Converting XML data to CSV...")
            csv_files = []
            xml_file_path = xml_file
            csv_output_dir = "data/apple_health_export/csv_output"  # Ensure this directory exists
            os.makedirs(csv_output_dir, exist_ok=True)
            
            csv_files += convert_xml_to_csv(xml_file_path, csv_output_dir, None)

            if csv_files:
                st.write("Preprocessing data...")
                data = preprocess_data(csv_files)

                st.success("Data loaded successfully!")
                visualize_data(data)

            else:
                st.error("No CSV files were generated from the XML.")
                logging.error("No CSV files were generated.")

        else:
            st.error("No XML files found in the ZIP archive.")
            logging.error("No XML files found in the ZIP archive.")

    # Clean up extracted files
    if os.path.exists("temp_data/"):
        logging.info("Cleaning up extracted files.")
        for file in os.listdir("temp_data/"):
            file_path = os.path.join("temp_data/", file)
            if os.path.isfile(file_path):  # Check if it is a file before removing
                os.remove(file_path)
        os.rmdir("temp_data/")

if __name__ == "__main__":
    main()
