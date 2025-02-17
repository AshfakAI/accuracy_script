import json
import os
import csv
from Levenshtein import ratio
global empty_ori_file
#empty_ori_file = []

def compare_json_files(original_file, test_file):
    # Load the original and test JSON data
    #print(original_file)
    #print(test_file)
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    results_accuracy = []
    results_mismatch = []


    # Correct and Incorrect count for langs and keywords

    correct_keyword_count = 0
    incorrect_keyword_count = 0

    # Mismatch details to be printed
    keyword_mismatches = []
    #if original_data['abstracts'] == [] and test_data['abstracts'] != []:
        
        #empty_ori_file.append(original_file)
    if original_data["publisher_copyright"] == "" and test_data["publisher_copyright"]== "":
        correct_keyword_count += 1
    else:
        try:
            similarity_score = ratio(str(original_data["publisher_copyright"]), str(test_data["publisher_copyright"]))
            print(similarity_score)
     
            if similarity_score>0.90:
            #if original_data["publisher_copyright"] == test_data["publisher_copyright"]:
                correct_keyword_count += 1

            else:
                    incorrect_keyword_count += 1
                    keyword_mismatches.append({
                            "publisher_copyright": "publisher_copyright",
                            "original_text": original_data["publisher_copyright"],
                            "test_text": test_data["publisher_copyright"]
                        })
                    # Collect mismatch details for keywords
                    keyword_mismatch_str = "; ".join([f'"publisher_copyright": {mismatch["original_text"]} -> {mismatch["test_text"]}' 
                                      for mismatch in keyword_mismatches])
                    results_mismatch.append([os.path.basename(test_file), 'publisher_copyright', keyword_mismatch_str])

        except:
            incorrect_keyword_count += 1
            #print(original_file)
            

    
    # Collect results for keywords
    results_accuracy.append([os.path.basename(test_file), 'publisher_copyright', correct_keyword_count, incorrect_keyword_count])



    return results_accuracy, results_mismatch,correct_keyword_count, incorrect_keyword_count

# Function to loop through the files in the original and test folders and compare them
def compare_folders(original_folder, test_folder):
    all_results_accuracy = []
    all_results_mismatch = []
    
    # Totals for accuracy calculation
    total_correct_keyword = 0
    total_incorrect_keyword = 0

    # Loop through each file in the original folder
    for filename in os.listdir(original_folder):
        original_file = os.path.join(original_folder, filename)
        test_file = os.path.join(test_folder, filename)

        if os.path.isfile(original_file) and os.path.isfile(test_file):
            result_accuracy, result_mismatch, correct_keyword_count, incorrect_keyword_count = compare_json_files(original_file, test_file)
            all_results_accuracy.extend(result_accuracy)
            all_results_mismatch.extend(result_mismatch)

            # Update total
            total_correct_keyword += correct_keyword_count
            total_incorrect_keyword += incorrect_keyword_count

    # Calculate overall accuracy for lang and keyword
    total_files = len([f for f in os.listdir(original_folder) if os.path.isfile(os.path.join(original_folder, f))])

    overall_keyword_accuracy = (total_correct_keyword / (total_correct_keyword + total_incorrect_keyword)) * 100 if total_correct_keyword + total_incorrect_keyword > 0 else 0

    # Print the overall accuracy results
    print(f"Overall accuracy for publisher_copyright: {overall_keyword_accuracy:.2f}%")

    # Save overall accuracy to the CSV file
    with open('output/publisher_copyright_accuracies.csv', 'w', newline='', encoding='utf-8') as accuracy_file:
        writer = csv.writer(accuracy_file)
        #writer.writerow(['filename', 'key name', 'correct count', 'incorrect count'])  # header
        #for row in all_results_accuracy:
            #writer.writerow(row)
        # Save the overall accuracy for lang and keyword at the end of the file
        writer.writerow(['Overall accuracy', 'publisher_copyright', f'{overall_keyword_accuracy:.2f}%', ''])

    # Save mismatch results to CSV
    with open('output/publisher_copyright_mismatch.csv', 'w', newline='', encoding='utf-8') as mismatch_file:
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
