import zipfile
import os
import json
import pandas as pd

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

# Function to compare abstracts in the new format
def compare_abstracts(original_data, test_data):
    mismatches = []
    
    # Iterate through each abstract in the 'abstracts' field (which is now an array of objects)
    original_abstracts = original_data.get("abstracts", [])
    test_abstracts = test_data.get("abstracts", [])
    
    # Compare abstracts for each language
    for original_abstract, test_abstract in zip(original_abstracts, test_abstracts):
        # Compare the 'text' field
        original_text = original_abstract.get("text", "Missing in original JSON")
        test_text = test_abstract.get("text", "Missing in test JSON")
        if original_text != test_text:
            mismatches.append({
                "field": "text",
                "original_value": original_text,
                "current_value": test_text
            })
        
        # Compare the 'lang' field (which is now a list)
        original_lang = original_abstract.get("lang", [])
        test_lang = test_abstract.get("lang", [])
        if original_lang != test_lang:
            mismatches.append({
                "field": "lang",
                "original_value": original_lang,
                "current_value": test_lang
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
        original_abstracts = original_jsons[file_name].get("abstracts", [])
        test_abstracts = test_jsons[file_name].get("abstracts", [])
        
        # Combine all keys in both abstracts (text and lang for each language)
        for original_abstract, test_abstract in zip(original_abstracts, test_abstracts):
            for key in ["text", "lang"]:
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
