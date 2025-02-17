import json
import os
import csv
from Levenshtein import ratio

# Function to compare the 'lang' keys and 'keyword' lists
def compare_json_files(original_file, test_file):
    # Load the original and test JSON data
    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    results_accuracy = []
    results_mismatch = []

    # Create dictionaries for keywords grouped by language
    original_keywords_by_lang = {entry['lang']: entry['text'] for entry in original_data['title']}
    test_keywords_by_lang = {entry['lang']: entry['text'] for entry in test_data['title']}

    # Correct and Incorrect count for langs and keywords
    correct_lang_count = 0
    incorrect_lang_count = 0
    correct_keyword_count = 0
    incorrect_keyword_count = 0

    # Mismatch details to be printed
    lang_mismatches = []
    keyword_mismatches = []

    if (original_data['title'] == []) and (test_data['title'] == []):
       correct_lang_count = 1
       correct_keyword_count =1
    else:
            
        # Compare langs first
        for lang in original_keywords_by_lang:
            if lang in test_keywords_by_lang:
                # Check if keyword sets are the same
                original_keywords_set = set(original_keywords_by_lang[lang])
                test_keywords_set = set(test_keywords_by_lang[lang])
                
                if original_keywords_set == test_keywords_set:
                    correct_lang_count += 1
                else:
                    incorrect_lang_count += 1
                    lang_mismatches.append(lang)
            else:
                incorrect_lang_count += 1
                lang_mismatches.append(lang)

        # Compare keywords for each lang
        for lang in original_keywords_by_lang:
            if lang in test_keywords_by_lang:
                # Compare keywords for that lang
                original_keywords_set = original_keywords_by_lang[lang]
                test_keywords_set = test_keywords_by_lang[lang]
                similarity_score = ratio(original_keywords_set, test_keywords_set)
                print(similarity_score)
                if similarity_score>0.9:
                    correct_keyword_count += 1
                else:
                    incorrect_keyword_count += 1
                    keyword_mismatches.append({
                        "lang": lang,
                        "original_text": original_keywords_by_lang[lang],
                        "test_text": test_keywords_by_lang[lang]
                    })
            else:
                # Missing language in test file
                incorrect_keyword_count += 1
                keyword_mismatches.append({
                    "lang": lang,
                    "original_text": original_keywords_by_lang[lang],
                    "test_text": 'Language missing in test file'
                })

    # Collect results for langs
    results_accuracy.append([os.path.basename(test_file), 'lang', correct_lang_count, incorrect_lang_count])
    
    # Collect results for keywords
    results_accuracy.append([os.path.basename(test_file), 'text', correct_keyword_count, incorrect_keyword_count])

    # Collect mismatch details for langs
    results_mismatch.append([os.path.basename(test_file), 'lang', ', '.join(lang_mismatches)])

    # Collect mismatch details for keywords
    keyword_mismatch_str = "; ".join([f'"text": {mismatch["original_text"]} -> {mismatch["test_text"]}' 
                                      for mismatch in keyword_mismatches])
    results_mismatch.append([os.path.basename(test_file), 'text', keyword_mismatch_str])

    return results_accuracy, results_mismatch, correct_lang_count, incorrect_lang_count, correct_keyword_count, incorrect_keyword_count

# Function to loop through the files in the original and test folders and compare them
def compare_folders(original_folder, test_folder):
    all_results_accuracy = []
    all_results_mismatch = []
    
    # Totals for accuracy calculation
    total_correct_lang = 0
    total_incorrect_lang = 0
    total_correct_keyword = 0
    total_incorrect_keyword = 0

    # Loop through each file in the original folder
    for filename in os.listdir(original_folder):
        original_file = os.path.join(original_folder, filename)
        test_file = os.path.join(test_folder, filename)

        if os.path.isfile(original_file) and os.path.isfile(test_file):
            result_accuracy, result_mismatch, correct_lang_count, incorrect_lang_count, correct_keyword_count, incorrect_keyword_count = compare_json_files(original_file, test_file)
            all_results_accuracy.extend(result_accuracy)
            all_results_mismatch.extend(result_mismatch)

            # Update totals
            total_correct_lang += correct_lang_count
            total_incorrect_lang += incorrect_lang_count
            total_correct_keyword += correct_keyword_count
            total_incorrect_keyword += incorrect_keyword_count

    # Calculate overall accuracy for lang and keyword
    total_files = len([f for f in os.listdir(original_folder) if os.path.isfile(os.path.join(original_folder, f))])

    overall_lang_accuracy = (total_correct_lang / (total_correct_lang + total_incorrect_lang)) * 100 if total_correct_lang + total_incorrect_lang > 0 else 0
    overall_keyword_accuracy = (total_correct_keyword / (total_correct_keyword + total_incorrect_keyword)) * 100 if total_correct_keyword + total_incorrect_keyword > 0 else 0

    # Print the overall accuracy results
    print(f"Overall accuracy for lang: {overall_lang_accuracy:.2f}%")
    print(f"Overall accuracy for text: {overall_keyword_accuracy:.2f}%")

    # Save overall accuracy to the CSV file
    with open('output/title_accuracy.csv', 'w', newline='', encoding='utf-8') as accuracy_file:
        writer = csv.writer(accuracy_file)
        #writer.writerow(['filename', 'key name', 'correct count', 'incorrect count'])  # header
        #for row in all_results_accuracy:
            #writer.writerow(row)
        # Save the overall accuracy for lang and keyword at the end of the file
        writer.writerow(['Overall accuracy', 'title_lang', f'{overall_lang_accuracy:.2f}%', ''])
        writer.writerow(['Overall accuracy', 'title_text', f'{overall_keyword_accuracy:.2f}%', ''])

    # Save mismatch results to CSV
    with open('output/text_mismatch.csv', 'w', newline='', encoding='utf-8') as mismatch_file:
        writer = csv.writer(mismatch_file)
        writer.writerow(['filename', 'key name', 'mismatch values'])  # header
        for row in all_results_mismatch:
            writer.writerow(row)

# Set the paths to your original and test folders
original_folder = 'original_extracted'
test_folder = 'test_extracted'

# Compare the folders
compare_folders(original_folder, test_folder)
