import zipfile
import os
import json
import pandas as pd
import csv

import json

# Read the paths from path.json
with open("path.json", "r", encoding="utf-8") as json_file:
    paths = json.load(json_file)


# Paths for the uploaded ZIP files
original_zip_path = paths['original_json_zip_path']
test_zip_path = paths['test_json_zip_path']

# Temporary extraction directories
original_extract_path = "original_extracted"
test_extract_path = "test_extracted"

# Extracting both zip files
with zipfile.ZipFile(original_zip_path, 'r') as original_zip:
    original_zip.extractall(original_extract_path)

with zipfile.ZipFile(test_zip_path, 'r') as test_zip:
    test_zip.extractall(test_extract_path)

# Function to load JSON from a directory
def load_json_files(directory):
    json_files = {}
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            with open(os.path.join(directory, file_name), 'r', encoding='utf-8') as file:
                json_files[file_name] = json.load(file)
    return json_files

# Load JSON data from both directories
original_jsons = load_json_files(original_extract_path)
test_jsons = load_json_files(test_extract_path)

# Compare keywords across files with the same name
results = []

for file_name in original_jsons:
    if file_name in test_jsons:
        original_keywords = set(original_jsons[file_name].get("keywords", []))
        test_keywords = set(test_jsons[file_name].get("keywords", []))
        
        correct_keywords = original_keywords & test_keywords
        incorrect_keywords = test_keywords - original_keywords
        
        results.append({
            "file_name": file_name,
            "total_keywords_in_test": len(test_keywords),
            "total_keywords_in_original": len(original_keywords),
            "correct_keywords_count": len(correct_keywords),
            "incorrect_keywords_count": len(incorrect_keywords),
            "correct_keywords": list(correct_keywords),
            "incorrect_keywords": list(incorrect_keywords),
        })

# Create a DataFrame from the results
results_df = pd.DataFrame(results)

# Calculate overall accuracy for keywords
total_correct_keywords = results_df['correct_keywords_count'].sum()
total_keywords_tested = results_df['total_keywords_in_test'].sum()
overall_accuracy = (total_correct_keywords / total_keywords_tested) * 100 if total_keywords_tested > 0 else 0

# Prepare the summarized output
summary_output = {
    "key name": "keywords",
    "% accuracy": f"{overall_accuracy:.2f}%",
    "total files": len(results_df)
}

# Ensure the output folder exists
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# Save the summary_output to a CSV file
summary_csv_path = os.path.join(output_folder, "keyword_accuracy_output.csv")

with open(summary_csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=summary_output.keys())
    writer.writeheader()
    writer.writerow(summary_output)

print(f"Summary output saved to '{summary_csv_path}'")
