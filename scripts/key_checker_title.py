import pandas as pd
import zipfile
import os
import json

import json

# Read the paths from path.json
with open("path.json", "r", encoding="utf-8") as json_file:
    paths = json.load(json_file)


# Paths for the uploaded ZIP files
original_zip_path = paths['original_json_zip_path']
test_zip_path = paths['test_json_zip_path']

original_extract_path = 'CAR_RED-Original_output'
test_extract_path = 'CAR_RED-output'

# Create directories if they don't exist
os.makedirs(original_extract_path, exist_ok=True)
os.makedirs(test_extract_path, exist_ok=True)

# Extract files from the zip archives
with zipfile.ZipFile(original_zip_path, 'r') as zip_ref:
    zip_ref.extractall(original_extract_path)

with zipfile.ZipFile(test_zip_path, 'r') as zip_ref:
    zip_ref.extractall(test_extract_path)

# List the files extracted for reference
original_files = os.listdir(original_extract_path)
test_files = os.listdir(test_extract_path)

# Prepare to compare JSON files
comparison_results = []

# Identify common files for comparison
common_files = set(original_files).intersection(set(test_files))

# Variables for accuracy calculation
total_files = len(common_files)
matching_files = 0

# Compare each common file
for file_name in common_files:
    original_file_path = os.path.join(original_extract_path, file_name)
    test_file_path = os.path.join(test_extract_path, file_name)
    
    # Use explicit encoding to avoid UnicodeDecodeError
    with open(original_file_path, 'r', encoding='utf-8') as original_file, open(test_file_path, 'r', encoding='utf-8') as test_file:
        original_data = json.load(original_file)
        test_data = json.load(test_file)
        
        # Check for "title" key and compare values
        original_title = original_data.get("title", None)
        test_title = test_data.get("title", None)
        
        if original_title == test_title:
            matching_files += 1
        else:
            comparison_results.append({
                "file_name": file_name,
                "key_name": "title",
                "test_value": test_title,
                "original_value": original_title
            })

# Calculate overall accuracy
accuracy = (matching_files / total_files) * 100 if total_files > 0 else 0

# Convert results to a DataFrame for better visualization
comparison_df = pd.DataFrame(comparison_results)

# Save detailed comparison in one CSV
output_csv_path_details = 'output/title_comparison_details.csv'
os.makedirs('output', exist_ok=True)
comparison_df.to_csv(output_csv_path_details, index=False)

# Save accuracy in another CSV with the specified format
accuracy_summary_df = pd.DataFrame([{"Sub-key": "title", "Average Accuracy (%)": f"{accuracy:.2f}"}])
output_csv_path_accuracy = 'output/title_accuracy_summary.csv'
accuracy_summary_df.to_csv(output_csv_path_accuracy, index=False)

# Print results
print(f"Detailed comparison saved to: {output_csv_path_details}")
print(f"Accuracy summary saved to: {output_csv_path_accuracy}")
