import pandas as pd
import zipfile
import os
import json
from Levenshtein import ratio

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
comparison_results_grant_text = []

# Identify common files for comparison
common_files = set(original_files).intersection(set(test_files))

# Variables for accuracy calculation
total_files = len(common_files)
matching_files_grant_text = 0

# Compare each common file for "grant_text"
for file_name in common_files:
    original_file_path = os.path.join(original_extract_path, file_name)
    test_file_path = os.path.join(test_extract_path, file_name)
    
    # Use explicit encoding to avoid UnicodeDecodeError
    with open(original_file_path, 'r', encoding='utf-8') as original_file, open(test_file_path, 'r', encoding='utf-8') as test_file:
        original_data = json.load(original_file)
        test_data = json.load(test_file)
        
        # Check for "grant_text" key and compare values
        original_grant_text = original_data.get("grant_text", None)
        test_grant_text = test_data.get("grant_text", None)
        # print(set(original_grant_text))
        # print(set(test_grant_text))
        
        #if original_grant_text == test_grant_text:
        #similarity_score = ratio(str(original_grant_text),str(test_grant_text))
        #print(similarity_score)
        if set(original_grant_text)==set(test_grant_text):
            matching_files_grant_text += 1
        else:
            comparison_results_grant_text.append({
                "file_name": file_name,
                "key_name": "grant_text",
                "test_value": test_grant_text,
                "original_value": original_grant_text
            })

# Calculate overall accuracy for "grant_text"
accuracy_grant_text = (matching_files_grant_text / total_files) * 100 if total_files > 0 else 0

# Convert results to a DataFrame for better visualization
comparison_df_grant_text = pd.DataFrame(comparison_results_grant_text)

# Save the detailed comparison results in one CSV file
comparison_csv_path = 'output/grant_text_comparison_results.csv'
os.makedirs('output', exist_ok=True)
comparison_df_grant_text.to_csv(comparison_csv_path, index=False)

# Save the accuracy value in a separate CSV file
accuracy_csv_path = 'output/grant_text_accuracy.csv'
accuracy_df = pd.DataFrame([{"key_name": "grant_text", "accuracy": f"{accuracy_grant_text:.2f}%"}])
accuracy_df.to_csv(accuracy_csv_path, index=False)

# Print file locations
print(f"Comparison results saved to: {comparison_csv_path}")
print(f"Accuracy report saved to: {accuracy_csv_path}")
