import zipfile
import os
import json
import pandas as pd
import csv


# Temporary extraction directories
original_extract_path = "original_extracted"
test_extract_path = "test_extracted"


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
global total_correct_keywords,total_incorrect_keywords
total_correct_keywords = 0
total_incorrect_keywords = 0


# Function to compare keywords (with language support)
def compare_keywords(original_data, test_data,file_name):
    global total_correct_keywords,total_incorrect_keywords

    mismatches = []
    
    original_keywords_list = original_data.get("keywords_list", [])
    test_keywords_list = test_data.get("keywords_list", [])
    
    def are_structures_equal_case_insensitive(list1, list2):
        if len(list1) != len(list2):
            return False
        
        for obj1, obj2 in zip(list1, list2):
            # Compare 'lang' (case-insensitive)
            if obj1['lang'].lower() != obj2['lang'].lower():
                return False
            
            # Compare 'keywords' as sets (case-insensitive, ignoring order)
            if set(kw.lower() for kw in obj1['keywords']) != set(kw.lower() for kw in obj2['keywords']):
                return False

        return True

    # Test
    result = are_structures_equal_case_insensitive(original_keywords_list,test_keywords_list)
    if result:
        total_correct_keywords +=1
    else:
        total_incorrect_keywords +=1
        mismatches.append({"file":file_name,
                           "original_value":original_keywords_list,
                           "test_value":test_keywords_list})
        
    return mismatches

# Compare keywords for all files
for file_name in original_jsons:
    if file_name in test_jsons:
        mismatches = compare_keywords(original_jsons[file_name], test_jsons[file_name],file_name)
        for mismatch in mismatches:
            results.append(mismatch)

# Create a DataFrame from the results
results_df = pd.DataFrame(results)
print(results_df)
# Calculate overall accuracy for keywords

overall_accuracy = (total_correct_keywords / (total_correct_keywords+total_incorrect_keywords)) * 100

# Prepare the summarized output (only key name and accuracy)
summary_output = {
    "key name": "keywords",
    "% accuracy": f"{overall_accuracy:.2f}%",
}

# Ensure the output folder exists
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# Save the summary_output to a CSV file
summary_csv_path = os.path.join(output_folder, "keywordlist_accuracy.csv")

with open(summary_csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=summary_output.keys())
    writer.writeheader()
    writer.writerow(summary_output)

print(f"Summary output saved to '{summary_csv_path}'")

# Save the detailed mismatches for keywords to a CSV
detailed_output_path = os.path.join(output_folder, "keyword_detailed_mismatches.csv")
results_df.to_csv(detailed_output_path, index=False)

print(f"Detailed keyword mismatches saved to '{detailed_output_path}'")
