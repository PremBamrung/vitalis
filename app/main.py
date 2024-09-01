import streamlit as st
import pandas as pd
import zipfile
import os
import logging
import matplotlib.pyplot as plt

from apple_health_exporter import AppleHealthExporter 

# Function to extract ZIP file
def extract_zip(uploaded_file):
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall("temp_data/")
        return [f for f in os.listdir("temp_data/") if f.endswith('.xml')]

# Function to convert XML to CSV
def convert_xml_to_csv(xml_file_path, csv_output_dir, include_tags):
    try:
        converter = AppleHealthExporter(xml_file_path, csv_output_dir, include_tags)
        converter.convert()
        return os.listdir(csv_output_dir)
    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return []

# Function to preprocess the data
def preprocess_data(files):
    combined_data = pd.DataFrame()
    for file in files:
        data = pd.read_csv(f"data/apple_health_export/csv_output/{file}")
        combined_data = pd.concat([combined_data, data], ignore_index=True)  
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
        st.write("Extracting data...")
        xml_files = extract_zip(uploaded_file)

        if xml_files:
            st.write("Converting XML data to CSV...")
            csv_files = []
            for xml_file in xml_files:
                xml_file_path = f"temp_data/{xml_file}"
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

        else:
            st.error("No XML files found in the ZIP archive.")

    # Clean up extracted files
    if os.path.exists("temp_data/"):
        for file in os.listdir("temp_data/"):
            os.remove(f"temp_data/{file}")
        os.rmdir("temp_data/")

if __name__ == "__main__":
    main()
