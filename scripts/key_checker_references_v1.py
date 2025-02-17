import json
import os
import csv
import zipfile
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


def compare_json_files(original_file, test_file):
    # Load the original and test JSON data
    #print(original_file)
    #print(test_file)
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    fulltext_results_accuracy = []
    source_text_results_accuracy = []
    results_mismatch = []


    # Correct and Incorrect count for langs and keywords

    correct_fulltext_count =  correct_source_text_count = 0
    incorrect_source_text_count = incorrect_fulltext_count = 0

    # Mismatch details to be printed
    keyword_mismatches = []
    #if original_data['abstracts'] == [] and test_data['abstracts'] != []:
        
        #empty_ori_file.append(original_file)
    original_references = original_data.get("references", [])
    test_references = test_data.get("references", [])
    if original_references == [] and test_references==[]:
            correct_fulltext_count += 1
            correct_source_text_count += 1
    else:
        try:
            # Extract 'ref_fulltext' into a list
            original_references_ref_fulltext_list = [item['ref_fulltext'] for item in original_references]
            # Extract 'source_text' into a list
            original_references_source_text_list = [item['source_text'] for item in original_references]


                        # Extract 'ref_fulltext' into a list
            test_references_ref_fulltext_list = [item['ref_fulltext'] for item in test_references]
            # Extract 'source_text' into a list
            test_references_source_text_list = [item['source_text'] for item in test_references]



            ref_fulltext_similarity_score = ratio(f"""{original_references_ref_fulltext_list}""", f"""{test_references_ref_fulltext_list}""")
            source_text_similarity_score = ratio(f"""{original_references_source_text_list}""", f"""{test_references_source_text_list}""")
     
            if ref_fulltext_similarity_score>=0.85:
            #if original_data["publisher_copyright"] == test_data["publisher_copyright"]:
                correct_fulltext_count += 1

            if ref_fulltext_similarity_score<0.85:
                    print(ref_fulltext_similarity_score)
                    incorrect_fulltext_count += 1
                    keyword_mismatches.append({
                            "subkey": "fulltext",
                            "original_text": f"""{original_references_ref_fulltext_list}""",
                            "test_text": f"""{test_references_ref_fulltext_list}"""
                        })
                    # Collect mismatch details for keywords
                    keyword_mismatch_str = "; ".join([f'"publisher_copyright": {mismatch["original_text"]} -> {mismatch["test_text"]}' 
                                      for mismatch in keyword_mismatches])
                    results_mismatch.append([os.path.basename(test_file), 'publisher_copyright', keyword_mismatch_str])

            if source_text_similarity_score>=0.85:
                correct_source_text_count += 1

            if source_text_similarity_score<0.85:
                    print(source_text_similarity_score)
                    incorrect_source_text_count += 1
                    keyword_mismatches.append({
                            "subkey": "source_text",
                            "original_text": f"""{original_references_source_text_list}""",
                            "test_text": f"""{test_references_source_text_list}"""
                        })
                    # Collect mismatch details for keywords
                    keyword_mismatch_str = "; ".join([f'"publisher_copyright": {mismatch["original_text"]} -> {mismatch["test_text"]}' 
                                      for mismatch in keyword_mismatches])
                    results_mismatch.append([os.path.basename(test_file), 'publisher_copyright', keyword_mismatch_str])

        except:
            incorrect_source_text_count += 1
            incorrect_fulltext_count += 1

            #print(original_file)
            

    
    # Collect results for keywords
    #fulltext_results_accuracy.append([os.path.basename(test_file), 'fulltext', correct_fulltext_count, incorrect_fulltext_count])
    #source_text_results_accuracy.append([os.path.basename(test_file), 'source_text', correct_source_text_count, incorrect_source_text_count])



    return fulltext_results_accuracy,source_text_results_accuracy, results_mismatch,incorrect_fulltext_count,incorrect_source_text_count,correct_fulltext_count,correct_source_text_count

# Function to loop through the files in the original and test folders and compare them
def compare_folders(original_folder, test_folder):
    # Totals for accuracy calculation
    total_correct_fulltext_count = 0
    total_incorrect_fulltext_count = 0
    total_correct_source_text_count = 0
    total_incorrect_source_text_count = 0
    all_results_mismatch = []

    # Loop through each file in the original folder
    for filename in os.listdir(original_folder):
        original_file = os.path.join(original_folder, filename)
        test_file = os.path.join(test_folder, filename)

        if os.path.isfile(original_file) and os.path.isfile(test_file):
            fulltext_results_accuracy,source_text_results_accuracy, results_mismatch,incorrect_fulltext_count,incorrect_source_text_count,correct_fulltext_count,correct_source_text_count = compare_json_files(original_file, test_file)
            # Update total
            total_correct_fulltext_count += correct_fulltext_count
            total_incorrect_fulltext_count += incorrect_fulltext_count

            total_correct_source_text_count += correct_source_text_count
            total_incorrect_source_text_count += incorrect_source_text_count
            all_results_mismatch.append(results_mismatch)

    # Calculate overall accuracy for lang and keyword
    #total_files = len([f for f in os.listdir(original_folder) if os.path.isfile(os.path.join(original_folder, f))])

    overall_fulltext_accuracy = (total_correct_fulltext_count / (total_correct_fulltext_count + total_incorrect_fulltext_count)) * 100 if total_correct_fulltext_count + total_incorrect_fulltext_count > 0 else 0
    overall_source_text_accuracy = (total_correct_source_text_count / (total_correct_source_text_count + total_incorrect_source_text_count)) * 100 if total_correct_source_text_count + total_incorrect_source_text_count > 0 else 0
    # Print the overall accuracy results
    print(f"Overall accuracy for fulltext: {overall_fulltext_accuracy:.2f}%")
    print(f"Overall accuracy for source_text: {overall_source_text_accuracy:.2f}%")

    # Save overall accuracy to the CSV file
    with open('output/references_subkey_accuracies.csv', 'w', newline='', encoding='utf-8') as accuracy_file:
        writer = csv.writer(accuracy_file)
        writer.writerow(['Overall accuracy', 'fulltext', f'{overall_fulltext_accuracy:.2f}%', ''])
        writer.writerow(['Overall accuracy', 'source_text', f'{overall_source_text_accuracy:.2f}%', ''])

    # Save mismatch results to CSV
    with open('output/references_mismatches_with_similarity.csv', 'w', newline='', encoding='utf-8') as mismatch_file:
        writer = csv.writer(mismatch_file)
        writer.writerow(['filename', 'key name', 'mismatch values'])  # header
        for row in all_results_mismatch:
            writer.writerow(row)

# Set the paths to your original and test folders
original_folder = 'original_extracted'
test_folder = 'test_extracted'

# Compare the folders
compare_folders(original_folder, test_folder)
#print(empty_ori_file)
