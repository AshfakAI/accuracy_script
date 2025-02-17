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

# Function to calculate accuracy and record mismatches
def calculate_accuracy_with_levenshtein(original_authors, test_authors, file_name, mismatches):
    original_dict = {author['author_id']: author for author in original_authors}
    test_dict = {author['author_id']: author for author in test_authors}

    subkey_matches = {}
    subkey_totals = {}

    for author_id in original_dict:
        if author_id in test_dict:
            original_author = original_dict[author_id]
            test_author = test_dict[author_id]
            for key in original_author:
                subkey_totals[key] = subkey_totals.get(key, 0) + 1
                if key in test_author:
                    similarity = ratio(str(original_author[key]), str(test_author[key])) * 100
                    if similarity >= 85:
                        subkey_matches[key] = subkey_matches.get(key, 0) + 1
                    else:
                        mismatches.append({
                            "file_name": file_name,
                            "missing_key": key,
                            "original_value": original_author[key],
                            "test_value": test_author[key]
                        })
                else:
                    mismatches.append({
                        "file_name": file_name,
                        "missing_key": key,
                        "original_value": original_author[key],
                        "test_value": "Key missing in test"
                    })
        else:
            for key, value in original_dict[author_id].items():
                subkey_totals[key] = subkey_totals.get(key, 0) + 1
                mismatches.append({
                    "file_name": file_name,
                    "missing_key": key,
                    "original_value": value,
                    "test_value": "Author missing in test"
                })

    for author_id in test_dict:
        if author_id not in original_dict:
            for key, value in test_dict[author_id].items():
                subkey_totals[key] = subkey_totals.get(key, 0) + 1
                mismatches.append({
                    "file_name": file_name,
                    "missing_key": key,
                    "original_value": "Author missing in original",
                    "test_value": value
                })

    subkey_accuracy = {
        key: (subkey_matches.get(key, 0) / total) * 100
        for key, total in subkey_totals.items()
    }

    return subkey_accuracy

# Compare authors subkeys for all JSON files
subkey_accuracies = {}
mismatches = []

for file_name in original_jsons:
    if file_name in test_jsons:
        original_authors = original_jsons[file_name].get("authors", [])
        test_authors = test_jsons[file_name].get("authors", [])
        subkey_accuracy = calculate_accuracy_with_levenshtein(original_authors, test_authors, file_name, mismatches)
        for subkey, accuracy in subkey_accuracy.items():
            if subkey not in subkey_accuracies:
                subkey_accuracies[subkey] = []
            subkey_accuracies[subkey].append(accuracy)

# Average accuracy for each sub-key
average_subkey_accuracies = {
    subkey: sum(accuracies) / len(accuracies)
    for subkey, accuracies in subkey_accuracies.items()
}

# Convert to DataFrame for display
subkey_accuracies_df = pd.DataFrame(list(average_subkey_accuracies.items()), columns=["Sub-key", "Average Accuracy (%)"])
print(subkey_accuracies_df)

# Ensure the output folder exists
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# Save the sub-key accuracy results
subkey_accuracies_df.to_csv("output/authors_subkey_accuracies.csv", index=False)
print("Sub-key accuracies saved to 'authors_subkey_accuracies.csv'")

# Save mismatches to a CSV file
mismatches_df = pd.DataFrame(mismatches)
mismatches_df.to_csv("output/authors_subkey_mismatches.csv", index=False)
print("Mismatches saved to 'authors_subkey_mismatches.csv'")
