import pandas as pd
import xml.etree.ElementTree as ET
import os
import logging
from collections import defaultdict
import time
from tqdm import tqdm 
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AppleHealthExporter:
    """A class to convert Apple Health XML data into CSV format.

    This class parses an Apple Health XML file, counts the occurrences of each tag,
    and saves the attributes of these tags into separate CSV files.
    
    Attributes:
        xml_file (str): The path to the Apple Health XML file to be parsed.
        output_dir (str): The directory where the CSV files will be saved.
        tag_count (defaultdict): Counts of each tag and their attributes.
    """

    def __init__(self, xml_file: str, output_dir: str, include_tags: Optional[List[str]] = None) -> None:
        """Initializes the AppleHealthExporter.

        Args:
            xml_file (str): The path to the Apple Health XML file to be parsed.
            output_dir (str): The directory where the CSV files will be saved.
            include_tags (List[str], optional): List of specific tags to include. If None, all tags are included.
        """
        if not os.path.isfile(xml_file):
            raise FileNotFoundError(f"The specified XML file does not exist: {xml_file}")
        
        if not os.path.isdir(output_dir):
            logging.warning(f"The output directory does not exist, it will be created: {output_dir}")
        
        self.xml_file = xml_file
        self.output_dir = output_dir
        self.tag_count: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.include_tags = include_tags

    def parse_xml(self) -> None:
        """Parses the Apple Health XML file and counts occurrences of each tag with detailed logging."""
        logging.info("Parsing XML file...")
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            logging.error(f"Error parsing XML file: {e}")
            return  # Exit if XML is not well-formed
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return  # Exit on unexpected error

        # Count tags
        logging.info("Counting tags in XML...")
        unique_tags = set()
        for element in tqdm(root.iter(), desc="Processing elements", unit="element"):
            if self.include_tags is None or element.tag in self.include_tags:
                self.tag_count[element.tag].append(element.attrib)
                unique_tags.add(element.tag)

        logging.info(f"Found {len(unique_tags)} unique tags in the XML file.")

    def create_output_directory(self) -> None:
        """Creates the output directory for CSV files if it doesn't already exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info(f"Output directory '{self.output_dir}' is ready.")

    def save_to_csv(self) -> None:
        """Processes tags and generates corresponding CSV files."""
        total_rows = 0
        
        logging.info("Processing tags and generating CSV files...")
        for tag, attribs in self.tag_count.items():
            tag_rows = len(attribs)
            total_rows += tag_rows
            
            # Prepare and log row for summary immediately
            logging.info(f"{tag:<40} {tag_rows:>40}")

            # Save to CSV
            df = pd.DataFrame(attribs)
            csv_file_path = os.path.join(self.output_dir, f"{tag}.csv")
            df.to_csv(csv_file_path, index=False)

        # Log total row count
        self.log_summary(total_rows)

    def log_summary(self, total_rows: int) -> None:
        """Logs the summary and execution time.

        Args:
            total_rows (int): The total number of rows processed.
        """
        separator = "-" * 80
        logging.info(separator)
        logging.info(f"{'Total number of rows :':<40} {total_rows:>40}")

    def convert(self) -> None:
        """Orchestrates the Apple Health XML to CSV conversion process."""
        start_time = time.time()
        
        self.create_output_directory()
        self.parse_xml()
        self.save_to_csv()

        # Calculate and log the execution time
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Execution time: {execution_time:.2f} seconds")


if __name__ == "__main__":
    xml_file_path = 'data/apple_health_export/export.xml'
    csv_output_dir = 'data/apple_health_export/csv_output'
    
    # Optional: Specify which tags to include
    include_tags = None  # Set to a list of tags to include, or None for all tags
    
    try:
        converter = AppleHealthExporter(xml_file_path, csv_output_dir, include_tags)
        converter.convert()
    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

