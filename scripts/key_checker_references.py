import zipfile
import os
import json
import pandas as pd
from Levenshtein import ratio

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

# Function to compare references, treating subkeys in references
def compare_references(original_data, test_data):
    mismatches = []
    original_references = original_data.get("references", [])
    test_references = test_data.get("references", [])
    
    # Compare the list elements of references
    max_len = max(len(original_references), len(test_references))
    for i in range(max_len):
        original_value = original_references[i] if i < len(original_references) else "Missing in original JSON"
        test_value = test_references[i] if i < len(test_references) else "Missing in test JSON"
        
        if isinstance(original_value, dict) and isinstance(test_value, dict):
            # Compare subkeys in the reference
            all_keys = set(original_value.keys()).union(set(test_value.keys()))
            for key in all_keys:
                orig_val = original_value.get(key, "Missing in original JSON")
                test_val = test_value.get(key, "Missing in test JSON")
                similarity_score = ratio(str(orig_val), str(test_val))  # Calculate similarity

                if similarity_score < 0.90:  # Threshold for mismatch
                    print(similarity_score)
                    print(orig_val)
                    print(test_val)
                    mismatches.append({
                        "index": i,
                        "field": key,
                        "original_value": orig_val,
                        "current_value": test_val,
                        "similarity_score": similarity_score
                    })
        else:
            similarity_score = ratio(str(original_value), str(test_value))  # Calculate similarity

            if similarity_score < 0.90:  # Threshold for mismatch
                print(original_value)
                print(test_value)
                print(similarity_score)
                mismatches.append({
                    "index": i,
                    "field": "reference",
                    "original_value": original_value,
                    "current_value": test_value,
                    "similarity_score": similarity_score
                })
    
    return mismatches

# Compare references subkeys for all JSON files
references_comparison_results = []

for file_name in original_jsons:
    if file_name in test_jsons:
        mismatches = compare_references(original_jsons[file_name], test_jsons[file_name])
        if mismatches:
            for mismatch in mismatches:
                references_comparison_results.append({
                    "file_name": file_name,
                    "key_name": "references",
                    "index": mismatch["index"],
                    "field": mismatch["field"],
                    "original_values": mismatch["original_value"],
                    "current_values": mismatch["current_value"],
                    "similarity_score": mismatch["similarity_score"]
                })

# Convert to DataFrame for detailed mismatches
references_mismatches_df = pd.DataFrame(references_comparison_results)

# Save the detailed mismatches to the output folder
references_output_path = os.path.join(output_folder, "references_mismatches_with_similarity.csv")
references_mismatches_df.to_csv(references_output_path, index=False)
print(f"Detailed references mismatches with similarity scores saved to '{references_output_path}'")

# Calculate accuracy for references subkeys
references_subkey_accuracies = {}

for file_name in original_jsons:
    if file_name in test_jsons:
        original_references = original_jsons[file_name].get("references", [])
        test_references = test_jsons[file_name].get("references", [])
        
        max_len = max(len(original_references), len(test_references))
        for i in range(max_len):
            original_value = original_references[i] if i < len(original_references) else {}
            test_value = test_references[i] if i < len(test_references) else {}
            
            if isinstance(original_value, dict) and isinstance(test_value, dict):
                all_keys = set(original_value.keys()).union(set(test_value.keys()))
                for key in all_keys:
                    if key not in references_subkey_accuracies:
                        references_subkey_accuracies[key] = {"matches": 0, "total": 0}
                    orig_val = original_value.get(key, None)
                    test_val = test_value.get(key, None)
                    references_subkey_accuracies[key]["total"] += 1
                    if orig_val == test_val:
                        references_subkey_accuracies[key]["matches"] += 1

# Calculate accuracy percentages for each subkey
average_references_subkey_accuracies = {
    key: (values["matches"] / values["total"]) * 100
    for key, values in references_subkey_accuracies.items()
}

# Convert subkey accuracies to DataFrame
references_accuracies_df = pd.DataFrame(
    list(average_references_subkey_accuracies.items()),
    columns=["Sub-key", "Average Accuracy (%)"]
)

# Save the subkey accuracies to the output folder
references_accuracies_output_path = os.path.join(output_folder, "references_subkey_accuracies.csv")
references_accuracies_df.to_csv(references_accuracies_output_path, index=False)
print(f"Sub-key accuracies saved to '{references_accuracies_output_path}'")
