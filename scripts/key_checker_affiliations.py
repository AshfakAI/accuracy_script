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

# Function to compare affiliations using affiliation_id
def compare_affiliations(original_data, test_data):
    mismatches = []
    original_affiliations = original_data.get("affiliations", [])
    test_affiliations = test_data.get("affiliations", [])
    
    # Convert affiliations into dictionaries keyed by affiliation_id
    original_dict = {affiliation.get("affiliation_id"): affiliation for affiliation in original_affiliations}
    test_dict = {affiliation.get("affiliation_id"): affiliation for affiliation in test_affiliations}
    
    # Compare based on affiliation_id
    all_ids = set(original_dict.keys()).union(set(test_dict.keys()))
    for aff_id in all_ids:
        original_affiliation = original_dict.get(aff_id, {})
        test_affiliation = test_dict.get(aff_id, {})
        
        if not original_affiliation or not test_affiliation:
            mismatches.append({
                "affiliation_id": aff_id,
                "field": "affiliation_id",
                "original_value": "Missing in original JSON" if not original_affiliation else original_affiliation,
                "current_value": "Missing in test JSON" if not test_affiliation else test_affiliation,
            })
        else:
            # Compare subkeys within each affiliation
            all_keys = set(original_affiliation.keys()).union(set(test_affiliation.keys()))
            for key in all_keys:
                original_value = original_affiliation.get(key, "Missing in original JSON")
                test_value = test_affiliation.get(key, "Missing in test JSON")
                if original_value != test_value:
                    mismatches.append({
                        "affiliation_id": aff_id,
                        "field": key,
                        "original_value": original_value,
                        "current_value": test_value,
                    })
    
    return mismatches

# Compare affiliations for all JSON files
affiliations_comparison_results = []

for file_name in original_jsons:
    if file_name in test_jsons:
        mismatches = compare_affiliations(original_jsons[file_name], test_jsons[file_name])
        if mismatches:
            for mismatch in mismatches:
                affiliations_comparison_results.append({
                    "file_name": file_name,
                    "key_name": "affiliations",
                    "affiliation_id": mismatch["affiliation_id"],
                    "field": mismatch["field"],
                    "original_values": mismatch["original_value"],
                    "current_values": mismatch["current_value"],
                })

# Convert to DataFrame for detailed mismatches
affiliations_mismatches_df = pd.DataFrame(affiliations_comparison_results)

# Save the detailed mismatches to the output folder
affiliations_output_path = os.path.join(output_folder, "affiliations_mismatches.csv")
affiliations_mismatches_df.to_csv(affiliations_output_path, index=False)
print(f"Detailed affiliations mismatches saved to '{affiliations_output_path}'")

# Calculate accuracy for affiliations subkeys
affiliations_subkey_accuracies = {}

for file_name in original_jsons:
    if file_name in test_jsons:
        original_affiliations = original_jsons[file_name].get("affiliations", [])
        test_affiliations = test_jsons[file_name].get("affiliations", [])
        
        # Convert affiliations into dictionaries keyed by affiliation_id
        original_dict = {affiliation.get("affiliation_id"): affiliation for affiliation in original_affiliations}
        test_dict = {affiliation.get("affiliation_id"): affiliation for affiliation in test_affiliations}
        
        # Compare subkeys for all affiliations
        all_ids = set(original_dict.keys()).union(set(test_dict.keys()))
        for aff_id in all_ids:
            original_affiliation = original_dict.get(aff_id, {})
            test_affiliation = test_dict.get(aff_id, {})
            
            if original_affiliation and test_affiliation:
                all_keys = set(original_affiliation.keys()).union(set(test_affiliation.keys()))
                for key in all_keys:
                    if key not in affiliations_subkey_accuracies:
                        affiliations_subkey_accuracies[key] = {"matches": 0, "total": 0}
                    original_value = original_affiliation.get(key, None)
                    test_value = test_affiliation.get(key, None)
                    affiliations_subkey_accuracies[key]["total"] += 1
                    if original_value == test_value:
                        affiliations_subkey_accuracies[key]["matches"] += 1

# Calculate accuracy percentages for each subkey
average_affiliations_subkey_accuracies = {
    key: (values["matches"] / values["total"]) * 100
    for key, values in affiliations_subkey_accuracies.items()
}

# Convert subkey accuracies to DataFrame
affiliations_accuracies_df = pd.DataFrame(
    list(average_affiliations_subkey_accuracies.items()),
    columns=["Sub-key", "Average Accuracy (%)"]
)

# Save the subkey accuracies to the output folder
affiliations_accuracies_output_path = os.path.join(output_folder, "affiliations_subkey_accuracies.csv")
affiliations_accuracies_df.to_csv(affiliations_accuracies_output_path, index=False)
print(f"Sub-key accuracies saved to '{affiliations_accuracies_output_path}'")
