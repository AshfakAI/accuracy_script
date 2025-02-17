import json
import shutil

import shutil
import os

# List of directory paths you want to delete
directories_to_delete = [
    'CAR_RED-Original_output',
    'CAR_RED-output',
    'original_extracted',
    'test_extracted'
]

for directory_path in directories_to_delete:
    try:
        # Check if the directory exists before attempting to delete
        if os.path.exists(directory_path):
            # Delete the directory and all of its contents
            shutil.rmtree(directory_path)
            print(f"The directory '{directory_path}' and all its contents have been deleted.")
        else:
            print(f"The directory '{directory_path}' does not exist.")

    except Exception as e:
        print(f"An error occurred while deleting '{directory_path}': {e}")






# Function to take user inputs and clean them
def save_cleaned_paths_to_json():
    # Taking input from the user
    original_json_zip_path = input("Enter the path for the original JSON data ZIP file: ")
    test_json_zip_path = input("Enter the path for the test JSON data ZIP file: ")
    output_json_path = input("Enter the output directory path where the result will be saved: ")

    # Clean the paths by removing any extra escaped quotes
    cleaned_paths_dict = {
        "original_json_zip_path": original_json_zip_path.strip("\""),
        "test_json_zip_path": test_json_zip_path.strip("\""),
        "output_json_path": output_json_path.strip("\"")
    }

    # Define the path to save the cleaned paths to "path.json"
    output_file_path = "path.json"

    # Saving the cleaned paths to "path.json"
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(cleaned_paths_dict, json_file, indent=4)

    print(f"Cleaned paths have been saved to {output_file_path}")

# Call the function to save the paths
save_cleaned_paths_to_json()

from scripts import key_checker_references_v1
from scripts import key_checker_affiliations_v1
from scripts import key_checker_abstract_v3
from scripts import key_checker_authors
from scripts import key_checker_grant_text
from scripts import key_checker_keywords_v3
from scripts import key_checker_title_v2
from scripts import key_checker_publisher_copyright


import pandas as pd
import os
import json

# Paths for the uploaded CSV files
uploaded_files = [
    'affiliations_subkey_accuracies.csv',
    'authors_subkey_accuracies.csv',
    'grant_text_accuracy.csv',
    'keywordlist_accuracy.csv',
    'references_subkey_accuracies.csv',
    'title_accuracy.csv',
    'abstract_subkey_accuracies.csv'
]

# Combine all CSV files into a single DataFrame
combined_df = pd.DataFrame()

for file_path in uploaded_files:
    df = pd.read_csv(f"output/{file_path}")
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# Remove columns where all values are null
cleaned_combined_df = combined_df.dropna(axis=1, how='all')

# Retain only "Sub-key" and "Average Accuracy (%)" columns
if "Sub-key" in cleaned_combined_df.columns and "Average Accuracy (%)" in cleaned_combined_df.columns:
    filtered_combined_df = cleaned_combined_df[["Sub-key", "Average Accuracy (%)"]]
else:
    # Handle missing expected columns gracefully
    filtered_combined_df = cleaned_combined_df

# Save the filtered combined DataFrame
output_csv_path = 'filtered_combined_accuracies.csv'
filtered_combined_df.to_csv(output_csv_path, index=False)

# Print results
print(f"Filtered combined accuracies saved to: {output_csv_path}")
