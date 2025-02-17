import zipfile
import os
import json
import pandas as pd

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

# Output folder for saving results
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

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

# Function to compare abstract fields including subkeys
def compare_abstracts(original_data, test_data):
    mismatches = []
    original_abstract = original_data.get("abstract", {})
    test_abstract = test_data.get("abstract", {})
    
    # Compare all subkeys in the abstract
    all_keys = set(original_abstract.keys()).union(set(test_abstract.keys()))
    for key in all_keys:
        original_value = original_abstract.get(key, "Missing in original JSON")
        test_value = test_abstract.get(key, "Missing in test JSON")
        if original_value != test_value:
            mismatches.append({
                "field": key,
                "original_value": original_value,
                "current_value": test_value
            })
    
    return mismatches

# Compare abstract subkeys for all JSON files
abstract_comparison_results = []

for file_name in original_jsons:
    if file_name in test_jsons:
        mismatches = compare_abstracts(original_jsons[file_name], test_jsons[file_name])
        if mismatches:
            for mismatch in mismatches:
                abstract_comparison_results.append({
                    "file_name": file_name,
                    "key_name": "abstract",
                    "field": mismatch["field"],
                    "original_values": mismatch["original_value"],
                    "current_values": mismatch["current_value"],
                })

# Convert to DataFrame for detailed mismatches
abstract_mismatches_df = pd.DataFrame(abstract_comparison_results)

# Save the detailed mismatches to the output folder
abstract_output_path = os.path.join(output_folder, "abstract_mismatches.csv")
abstract_mismatches_df.to_csv(abstract_output_path, index=False)
print(f"Detailed abstract mismatches saved to '{abstract_output_path}'")

# Calculate accuracy for "abstract" subkeys
abstract_subkey_accuracies = {}

for file_name in original_jsons:
    if file_name in test_jsons:
        original_abstract = original_jsons[file_name].get("abstract", {})
        test_abstract = test_jsons[file_name].get("abstract", {})
        
        # Combine all keys in both abstracts
        all_keys = set(original_abstract.keys()).union(set(test_abstract.keys()))
        for key in all_keys:
            if key not in abstract_subkey_accuracies:
                abstract_subkey_accuracies[key] = {"matches": 0, "total": 0}
            original_value = original_abstract.get(key, None)
            test_value = test_abstract.get(key, None)
            
            # Increment total and match counts
            abstract_subkey_accuracies[key]["total"] += 1
            if original_value == test_value:
                abstract_subkey_accuracies[key]["matches"] += 1

# Calculate accuracy percentages for each subkey
average_abstract_subkey_accuracies = {
    key: (values["matches"] / values["total"]) * 100
    for key, values in abstract_subkey_accuracies.items()
}

# Convert subkey accuracies to DataFrame
abstract_accuracies_df = pd.DataFrame(
    list(average_abstract_subkey_accuracies.items()),
    columns=["Sub-key", "Average Accuracy (%)"]
)

# Save the subkey accuracies to the output folder
abstract_accuracies_output_path = os.path.join(output_folder, "abstract_subkey_accuracies.csv")
abstract_accuracies_df.to_csv(abstract_accuracies_output_path, index=False)
print(f"Sub-key accuracies saved to '{abstract_accuracies_output_path}'")
