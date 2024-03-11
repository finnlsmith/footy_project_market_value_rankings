# %%
import os
import csv
import pandas as pd
from difflib import get_close_matches
import numpy as np
import re
from transliterate import translit
from unidecode import unidecode
import Levenshtein
import requests
import bs4
from bs4 import BeautifulSoup 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from datetime import datetime

from urllib.parse import urlsplit

import wikipediaapi

import wikipedia

from urllib.parse import urlparse

import difflib

from datetime import datetime

import calendar

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from datetime import datetime, timedelta



# %% [markdown]
# ### Functions for salary lookup

# %% [markdown]
# ### GETTING NULL NAMES - SALARIES

# %%

def load_csv_dataset(file_path):
    return pd.read_csv(file_path)
result_names_null = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/footy_project_market_value_rankings/create_dataset_1/nullnames_salaries.csv')
result_names_null = list(result_names_null['Name'])

result_names_null_values = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/footy_project_market_value_rankings/create_dataset_1/nullnames_values.csv')
result_names_null_values = list(result_names_null_values['Name'])

# Usage
leagues_salary = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/footy_project_market_value_rankings/create_dataset_1/latest_capology_data_money_fixed.csv')

#leagues_value = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/most_updated_transfermarkt_dataset.csv')
#leagues_value = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/Fixed TransferMarkt Market Values - MarketValues.csv')
leagues_value = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/footy_project_market_value_rankings/create_dataset_1/Most Updated Edited Transfermarkt Dataset.csv')
leagues_value_large = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/footy_project_market_value_rankings/create_dataset_1/most_updated_transfermarkt_dataset.csv')

countries_codes = load_csv_dataset('/Users/finneganlaister-smith/Downloads/DEV ENVIRONMENT/data-science-jupyter-template-main/footy_project_market_value_rankings/create_dataset_1/countries_and_codes.csv')


def get_names_with_conditions_salary(df):
    # Create an empty list to store names that satisfy the conditions
    result_names = []

    # Iterate through unique names in the DataFrame
    for name in df['Name'].unique():
        # Create a subset of the DataFrame for the current name
        subset = df[df['Name'] == name].reset_index()

        # Check conditions: length of subset is 1 and 'Weekly Salary' is NaN
        if len(subset) == 1 and pd.isna(subset['Weekly Salary'].iloc[0]):
            result_names.append(name)

    return result_names

#result_names_null = get_names_with_conditions_salary(leagues_salary)

# %% [markdown]
# ### single name - string process / lookup - Functions

# %%
# def is_cyrillic(input_string):
#     # Check if the string contains non-ASCII characters
#     return not input_string.isascii()
def is_cyrillic(input_string):
    # Cyrillic Unicode range
    cyrillic_range = range(0x0400, 0x04FF + 1)
    # Allowed characters
    allowed_chars = set('.\'`0123456789-' + ''.join(chr(c) for c in cyrillic_range))

    # Iterate through each character in the input string
    for char in input_string:
        # Skip whitespace characters
        if char.isspace():
            continue
        # Check if the character is not allowed
        if char not in allowed_chars:
            return False  # Return False if any disallowed character is found
    
    return True  # Return True if all characters are allowed

def cyrillic_to_latin(input_string):
    try:
        # Use the "translit" function to convert Cyrillic to Latin
        latin_string = translit(input_string, 'ru', reversed=True)
        return latin_string
    except Exception as e:
        # Handle exceptions, e.g., if the input is not valid Cyrillic
        print(f"Error: {e}")
        return input_string

def find_best_match(array, final_tokens, ORIGINAL_STRING):
    # Concatenate final tokens to form the expected full name
    expected_name = ' '.join(final_tokens)
    
    # Filter names that start with the initial letter
    filtered_names = [name for name in array if name.startswith(final_tokens[0])]
    
    if not filtered_names:
        if(len(final_tokens) == 1):
            filtered_names = [name for name in array if name.endswith(final_tokens[-1])]
            final_tokens = [final_tokens[-1]]
        # Try switching the order of final tokens
        else:
            filtered_names = [name for name in array if name.startswith(final_tokens[1])]
            final_tokens = [final_tokens[1], final_tokens[0]]
    
    if not filtered_names:
        return None  # No matching names found
    
    # Check if the ORIGINAL_STRING contains a backtick/apostrophe
    has_backtick_apostrophe = "'" in ORIGINAL_STRING or "`" in ORIGINAL_STRING
    
    # Filter names based on the presence of a backtick/apostrophe
    filtered_names = [name for name in filtered_names if "'" in name or "`" in name] if has_backtick_apostrophe else filtered_names
    
    if not filtered_names:
        return None  # No matching names found
    
    # Calculate Levenshtein distance between the expected name and each remaining name
    distances = [Levenshtein.distance(unidecode(expected_name), unidecode(name.replace(" ", ""))) for name in filtered_names]
    
        # Find the minimum distance
    min_distance = min(distances)

    # Find the indices of names with the minimum distance
    min_distance_indices = [i for i, distance in enumerate(distances) if distance == min_distance]

    # Return all names with the minimum distance
    result_names = [filtered_names[i] for i in min_distance_indices]

    # Print or return the result based on your requirement
    return result_names
    #print(result_names)


def remove_leading_jersey_num(input_string):
    return re.sub(r'^\d{1,2}[. ]', '', input_string)

def process_leading_initial_token(tokens):
    final_string = ""
    if len(tokens) >= 1 and not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ]{2,}$', tokens[0]):
        initial_match = re.match(r'^([A-Za-zÀ-ÖØ-öø-ÿ]+\.)+$|[A-Za-zÀ-ÖØ-öø-ÿ]\.$|[A-Za-zÀ-ÖØ-öø-ÿ]$', tokens[0])
        if initial_match:
            final_string += initial_match.group()
    return final_string

def process_main_phrase(tokens):
    main_phrase = " ".join(word for word in tokens if len("".join(char for char in word if char.isalpha())) >= 2)
    return main_phrase

def process_end_initial(tokens, final_string):
    if len(tokens) >= 2 and not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ]{2,}$', tokens[1]):
        end_initial_match = re.match(r'^([A-Za-zÀ-ÖØ-öø-ÿ]+\.)+$|[A-Za-zÀ-ÖØ-öø-ÿ]\.$|[A-Za-zÀ-ÖØ-öø-ÿ]$', tokens[1])
        if end_initial_match:
            final_string = "".join(char for char in end_initial_match.group() if char.isalpha()) + " " + final_string
    return final_string


def process_long_end_initial(tokens, final_string):
    if len(tokens[-1]) >= 3 and tokens[-1].endswith("."):
        trailing_token_is_long_starting_initial = True
        final_string = final_string.replace(tokens[-1], "")
        final_string = final_string[:-1]
    return final_string

def process_hyphenated_last_initial(tokens, final_string):
    if '-' in tokens[-1]:
        parts = tokens[-1].split('-')
        if len(parts[0]) >= 2 and len(parts[1]) >= 2:
            return final_string
        else:
            final_string = tokens[-1] + ' ' + final_string
            tokens_hyphen_case = final_string.split()
            if(tokens_hyphen_case[0] == tokens_hyphen_case[-1]):
                final_string = final_string[:-len(tokens_hyphen_case[-1])].rstrip()
    return final_string

def process_hyphenated_first_initial(tokens, final_string):
    if '-' in tokens[0]:
        parts = tokens[0].split('-')
        if len(parts[0]) >= 2 and len(parts[1]) >= 2:
            return final_string
        else:
            final_string = tokens[0] + ' ' + final_string
    return final_string

def process_accent_tokens(final_string):
    final_tokens = [re.sub(r'[^A-Za-zÀ-ÖØ-öø-ÿČřäáāņļćčšðŽž\'`ūńæŁęúâąșăãýōţțğÇçüů-]', '', token) for token in final_string.split()]
    return final_tokens

def process_multiple_initials(final_tokens):
    if len(final_tokens[0]) >= 2 and final_tokens[0].isupper():
        final_tokens[0] = final_tokens[0][0]
    return final_tokens

def process_string_newest_ii(input_string, competition):
    cleaned_string = remove_leading_jersey_num(input_string)
    tokens = cleaned_string.split()
    final_string = ""

    ##FILTER FOR WHAT

    final_string += process_leading_initial_token(tokens)
    #print('added leading initial', final_string)

    main_phrase = process_main_phrase(tokens)
    if main_phrase:
        final_string += " " + main_phrase
    #print('added main phrase', final_string)

    final_string = process_end_initial(tokens, final_string)
    #print('added end initial', final_string)

    final_string = process_long_end_initial(tokens, final_string)
    #print('last initial longer than 1 letter', final_string)

    final_string = process_hyphenated_last_initial(tokens, final_string)
    #print('hyphenated last initial', final_string)
    final_string = process_hyphenated_first_initial(tokens, final_string)
    #print('hyphenated first initial', final_string)

    final_tokens = process_accent_tokens(final_string)
    #print('process accents, tokens:', final_tokens)

    final_tokens = process_multiple_initials(final_tokens)
    #print('process multiple initials, tokens: ', final_tokens)

    joined_string = " ".join(final_tokens)
    return joined_string, final_tokens

    #return " ".join(final_tokens)

def extract_first_name(match_apostrophes_accounted, lastname_match):
    # Check if lastname_match is part of match_apostrophes_accounted
    if lastname_match in match_apostrophes_accounted:
        # Split the string using lastname_match as the separator
        first_name = match_apostrophes_accounted.split(lastname_match)[0].strip()
        return first_name
    else:
        # Handle the case where lastname_match is not found in match_apostrophes_accounted
        print(f"{lastname_match} not found in {match_apostrophes_accounted}")
        return None
    
def add_backticks(lastname_match, original_string_nojersey):
    # Find the indices of backticks/apostrophes in the original string
    special_indices = [i for i, char in enumerate(original_string_nojersey) if char in ("`", "'")]

    # Add backticks in the corresponding places in the last name match
    for index in special_indices:
        # Check if the index is within the range of the last_name_match
        if 0 <= index < len(lastname_match):
            # Insert backtick in the appropriate position
            lastname_match = lastname_match[:index] + original_string_nojersey[index] + lastname_match[index:]

    return lastname_match

def find_closest_string_newEST(input_string, string_list, input_final_tokens, ORIGINAL_NAME_STRING):
    #replace nationality name list with string_list
    #replace string_for_search with input_string 
    #replace final_tokens with input_final_tokens
    #replace input_string with ORIGINAL_NAME_STRING
    matching_end_strings = [s for s in string_list if s.endswith(input_string)]
    if matching_end_strings:
        return matching_end_strings
        
    if len(input_final_tokens) > 1 and len(input_final_tokens[0]) <= 2:
        start_with_end_strings = [s for s in string_list if s.startswith(input_final_tokens[0]) and s.endswith(input_string)]
        if start_with_end_strings:
            return start_with_end_strings

    closest_match = get_close_matches(input_string, string_list, n=1, cutoff=0.8)
    print(closest_match, get_close_matches(input_string, string_list, n=1, cutoff=0.7))

    closest_match_4 = []
    closest_match_3 = []
    closest_match_2 = []
    index_match = ""
    matching_indices = []

    if closest_match:
       
        return closest_match[0]
    else:
        #Reduce match constraints
        closest_match_ii = get_close_matches(input_string, string_list)
        #Produces a match
        if closest_match_ii:
            if((type(closest_match_ii) == list) & (len(closest_match_ii) >= 2)):
                #Closest match II returns 1 name
                original_string_nojersey = re.sub(r'^\d+(\.)?\s*', '', ORIGINAL_NAME_STRING)
                #Find best match from set of names
                result_1 = find_best_match(closest_match_ii, input_final_tokens, original_string_nojersey)
                if(type(result_1) == list):
                    closest_match_ii = result_1
                    #print(closest_match_ii)
                    return closest_match_ii
                elif(pd.isna(result_1)):
                    #none of the names from closest match ii were a good match
                    0==0
                    print('no results here')
                else:
                    #1 of the names from closest match ii were a good match
                    #print('closest match ii best match: ' + result_1)
                    closest_match_ii = result_1
                    #RETURN HERE
                    return closest_match_ii
            else:
                #Closest match II returns 1 name
                #print('1 match ' + closest_match_ii[0])
                #RETURN HERE
                return closest_match_ii[0]
        else:
            # no close matches
            last_word = input_string.split()[-1]
            #KREJCI CASE 
            if(last_word == 'Krejčí'):
                match_krejci = get_close_matches(last_word, string_list, n=1, cutoff=0.380952)
                if(type(match_krejci) == list):
                    if(len(match_krejci) == 1):
                        match_krejci = match_krejci[0]
                        return match_krejci


            # Return strings from the list if the last word is in those strings
            matching_strings = [s for s in string_list if last_word in s]

            if matching_strings:
                if(len(matching_strings) == 1):
                    #print('match string ' + matching_strings[0])
                    #RETURN HERE
                    return matching_strings[0]
                else:
                    #print(matching_strings)
                    setofmatches = matching_strings
                    print('this is a set here')
                    return setofmatches
                    
        #elif(closest_match):       
        if(closest_match): #NOT GONNA GET HERE. 
            #RETURN
            print('1', closest_match[0], closest_match[0] in string_list)
        elif(closest_match_ii):
            if(type(closest_match_ii) == str):
                print(closest_match_ii, closest_match_ii in string_list)
                return closest_match_ii
            #RETURN
            else:
                #print('ii', closest_match_ii, )#, closest_match_ii[0] in string_list
                return closest_match_ii
        elif(closest_match_3):
            #RETURN
            print('3', closest_match_3[0], closest_match_3[0] in string_list)
        elif(closest_match_2):
            #RETURN
            print('2', closest_match_2[0], closest_match_2[0] in string_list)
        elif(closest_match_4):
            #RETURN
            print('4', closest_match_4[0], closest_match_4[0] in string_list)
        # elif(index_match != ""):
        #     #RETURN
        #     print('end ' + index_match + ORIGINAL_NAME_STRING, matching_indices)
        #     return(index_match)
        else:
            #RETURN
            return("No close match found.")
            #print("No close match found.")

def filter_candidates(NAMESTRING, LISTCANDIDATES):
    # Get the first token of the NAMESTRING
    first_token = re.split(r'\s', NAMESTRING)[0]

    # Create a regex pattern for matching candidates that start with the first token
    pattern = re.compile(fr'^{re.escape(first_token)}', re.IGNORECASE)

    # Filter candidates based on the pattern
    filtered_candidates = list(filter(lambda x: re.match(pattern, x), LISTCANDIDATES))

    return filtered_candidates

def remove_accents_from_strings(input_array):
    # Ensure the input is a numpy array
    if not isinstance(input_array, np.ndarray) or input_array.dtype != np.dtype('O'):
        raise ValueError("Input must be a NumPy array of strings")

    # Define a function to remove accents from a single string
    def remove_accents_single_string(s):
        return unidecode(s)

    # Vectorize the function to apply it element-wise to the array
    remove_accents_vectorized = np.vectorize(remove_accents_single_string)

    # Apply the vectorized function to each element in the array
    result_array = remove_accents_vectorized(input_array)

    return result_array

def find_names_with_accents(target_name, name_array):
    # Ensure the input is a numpy array
    if not isinstance(name_array, np.ndarray) or name_array.dtype != np.dtype('O'):
        raise ValueError("Input must be a NumPy array of strings")

    if (type(target_name) == list) & (len(target_name) == 1):
        target_name = target_name[0]
    # Remove accents from the target name
    #print('name is ', target_name)
    target_name_without_accents = unidecode(target_name)

    # Define a function to check if a name with accents matches the target name
    def has_accent_match(name):
        return unidecode(name) == target_name_without_accents

    # Vectorize the function to apply it element-wise to the array
    has_accent_match_vectorized = np.vectorize(has_accent_match)

    # Apply the vectorized function to each element in the array
    matching_names = name_array[has_accent_match_vectorized(name_array)]

    if(len(matching_names) == 1):
        return matching_names[0]

    return matching_names

def remove_apostrophes_backticks(input_array):
    # Ensure the input is a numpy array
    if not isinstance(input_array, np.ndarray) or input_array.dtype != np.dtype('O'):
        raise ValueError("Input must be a NumPy array of strings")

    # Define a function to remove apostrophes and backticks from a single string
    def remove_chars_single_string(s):
        return np.char.replace(np.char.replace(s, "'", ''), "`", '')

    # Vectorize the function to apply it element-wise to the array
    remove_chars_vectorized = np.vectorize(remove_chars_single_string)

    # Apply the vectorized function to each element in the array
    result_array = remove_chars_vectorized(input_array)

    return result_array

def transform_korean_name(name):
    # Split the name into parts
    parts = name.split()

    # Check if the name has at least two parts
    if len(parts) >= 2:
        # Format the name as "Ja-cheol Koo"
        transformed_name = f"{parts[1].capitalize()}-{parts[0].capitalize()}"
        return transformed_name
    else:
        # Return the original name if it doesn't have at least two parts
        return name
    
def remove_apostrophes_backticks_single_string(input_string):
    # Ensure the input is a string
    if not isinstance(input_string, str):
        raise ValueError("Input must be a string")

    # Define a function to remove apostrophes and backticks from a single string
    def remove_chars_single_string(s):
        return s.replace("'", '').replace("`", '')

    # Apply the function to the input string
    result_string = remove_chars_single_string(input_string)

    return result_string

def filter_names_first_initial_lastname(database, search_string):
    # Filter out non-string elements from the database
    string_database = [str(item) for item in database if isinstance(item, str)]
    
    # Convert search string to lowercase for case-insensitive matching
    search_string_lower = search_string.lower()
    
    # Split the search string into parts
    parts = search_string_lower.split()
    
    # Filter names based on conditions
    filtered_names = [name for name in string_database if all(part in name.lower() for part in parts)]
    
    return filtered_names

# %% [markdown]
# ### GETTING NULL NAMES - VALUES

# %%
def get_names_with_conditions_values(df):
    # Create an empty list to store names that satisfy the conditions
    result_names = []

    # Iterate through unique names in the DataFrame
    for name in df['Name'].unique():
        # Create a subset of the DataFrame for the current name
        subset = df[df['Name'] == name].reset_index()

        # Check conditions: length of subset is 1 and 'Market Value' is equal to '-'
        if len(subset) == 1 and subset['Market Value'].iloc[0] == '-':
            result_names.append(name)

    return result_names

#result_names_null_values = get_names_with_conditions_values(leagues_value)


# %% [markdown]
# ## Find Name in Database / use online search / impute - FUNCTIONS

# %% [markdown]
# ### Helper methods

def has_c_with_accent_and_capital(string):
    pattern = r'([cćčç])([A-Z])'
    match = re.search(pattern, string)
    if match:
        # Inserting a space after the 'c' with an accent
        modified_string = re.sub(pattern, r'\1 \2', string)
        return True, modified_string
    else:
        return False, string

# %%
def lookup_name(input_name, input_nationality, input_match_date, using_salaries_boolean, competition):

    example_problem = input_name
    natl_test = input_nationality
    input_year_test = input_match_date

    if(using_salaries_boolean == True): #salaries_or_values == 'salary'
        database_name = leagues_salary
        money_column_name = "Inflation-Adjusted Yearly Salary"
    elif(using_salaries_boolean == False): #salaries_or_values == 'value'
        database_name = leagues_value
        money_column_name = "Market Value"

        
    candidate_name = ""
    candidates_set = []
    match_type = ""

    nationality_code = countries_codes[countries_codes['Country'] == natl_test][' Code'].unique()[0]
    #players from their country 
    #dataset_nationality = database_name[database_name['Nationality'] == f"{natl_test}"]['Name'].unique()
    dataset_nationality = database_name[database_name['Team 1 Code'] == f"{nationality_code}"]['Name'].unique()
    

    if(is_cyrillic(example_problem)):
        #change from cyrillic to english
        print('ride')
        #example_problem = cyrillic_to_latin(example_problem)
        match_type = "cyrillic"
        return 0, match_type, example_problem
        

    print(f"searching for {example_problem}")

    pattern_found, example_problem = has_c_with_accent_and_capital(example_problem)
    if pattern_found:
        print("Pattern found in the string.")
        print("Modified string:", example_problem)
    else:
        print("Pattern not found in the string.")

    print(example_problem, competition)
    search_name, final_tokens_name = process_string_newest_ii(example_problem, competition)
    print(f'search name: {search_name}, ft name: {final_tokens_name}')

    if(len(dataset_nationality) == 0):
        print(f'length of {input_nationality} dataset is 0')
        match_type = "none"
        return 0, match_type, search_name
    else:

        #look their name up in the list of names from their nationality. 
        result = find_closest_string_newEST(search_name, dataset_nationality, final_tokens_name, example_problem)
        if((type(result) == list) & (len(result) >= 2)):
            candidates_set = result
        elif(result[0] in dataset_nationality):
            candidate_name = result[0]
        elif(result in dataset_nationality):
            #print(result)
            #RETURN 
            candidate_name = result
        else:
            #no match found after first call 
            #print('no initial match found: ', search_name)
            nationality_names_accents_removed = remove_accents_from_strings(dataset_nationality)
            match_accent_accounted = find_closest_string_newEST(search_name, nationality_names_accents_removed,final_tokens_name, example_problem)
            #print('here i am', match_accent_accounted, type(match_accent_accounted))
            if type(match_accent_accounted) == list:
                if len(match_accent_accounted) >= 2:
                    candidates_set = [word for word in match_accent_accounted if word in nationality_names_accents_removed]
                else:
                    match_accent_accounted = match_accent_accounted[0]
            #print('now match is ', match_accent_accounted)
            if(match_accent_accounted in nationality_names_accents_removed):
                #print(match_accent_accounted)
                matching_names_with_accents = find_names_with_accents(match_accent_accounted, dataset_nationality)
                if(type(matching_names_with_accents) == str):
                    print('this is single match', matching_names_with_accents)
                    #RETURN
                    candidate_name = matching_names_with_accents
                elif(len(matching_names_with_accents) == 0):
                    print(f'accent-less name found: {match_accent_accounted}. But name not in original dataset')
                else:
                    print(f'multiple names found after adding accents: {matching_names_with_accents}')
                    candidates_set = matching_names_with_accents

                #MAKE SURE THE NAME WITH ACCENTS IS IN DATASET NATIONALITY 
            else:
                #print('no accent match found:', search_name)

                dataset_nationality_backticks = remove_apostrophes_backticks(dataset_nationality) #dataset_nationality_updated
                match_apostrophes_accounted = find_closest_string_newEST(search_name, dataset_nationality_backticks,final_tokens_name, example_problem)
            
                if(match_apostrophes_accounted in dataset_nationality_backticks):

                    lastname_match = match_apostrophes_accounted.split()[-1] 
                    original_string_nojersey = re.sub(r'^\d+(\.)?\s*', '', example_problem)
                    correct_lastname = add_backticks(lastname_match, original_string_nojersey)
                    correct_firstname = extract_first_name(match_apostrophes_accounted, lastname_match)
                    
                    correct_name_full = correct_firstname + ' ' + correct_lastname

                    if(correct_name_full in dataset_nationality):
                        print(correct_name_full)
                        #RETURN
                        candidate_name = correct_name_full
                    elif(correct_name_full.replace('`', "'") in dataset_nationality):
                        print(correct_name_full.replace('`', "'"))
                        #RETURN
                        candidate_name = correct_name_full.replace('`', "'")
                    elif(type(match_apostrophes_accounted) != str):
                        print(f'multiple names found after adding backticks: {match_apostrophes_accounted}')
                        candidates_set = match_apostrophes_accounted
                    else:
                        print(f'backtick-less name found: {match_apostrophes_accounted}. But name not in original dataset')
                
                else:
                    0==0
                    #print('no backtick match found:', search_name)

        if(candidate_name != ""):
            match_type = "single"
            return candidate_name, match_type, search_name
        else:
            if(candidates_set != []):
                match_type = "multiple"
                return candidates_set, match_type, search_name
            else:
                match_type = "none"
                return 0, match_type, search_name

# %%

def find_money_info_from_name(input_name, input_nationality, input_match_date, using_salaries_boolean, salary_null_name_list, value_null_name_list):

    candidate_name = input_name
    input_year_test = input_match_date

    if(using_salaries_boolean == True): #salaries_or_values
        database_name = leagues_salary
        money_column_name = "Inflation-Adjusted Yearly Salary"
        nulldb_name_list = salary_null_name_list
    elif(using_salaries_boolean == False): #salaries_or_values
        database_name = leagues_value
        money_column_name = "Market Value"
        nulldb_name_list = value_null_name_list

    if '.' in input_year_test:
        yearstr = input_year_test.split(".")[2]
        full_num = int('20' + yearstr)
    elif '-' in input_year_test:
        if len(input_year_test.split("-")[2]) == 4:
            yearstr = input_year_test.split("-")[2] #this is a 4 digit number
            full_num = int(yearstr)
        elif len(input_year_test.split("-")[2]) == 2:
            if len(input_year_test.split("-")[0]) == 4:
                yearstr = input_year_test.split("-")[0]
                full_num = int(yearstr)
            else:
                yearstr = input_year_test.split("-")[2] #this is a 2 digit number
                full_num = int('20' + yearstr)
        else:
            print('broke on year parsing', input_year_test.split("-"))
        # elif len(input_year_test.split("-")[0]) == 4:
            # yearstr = input_year_test.split("-")[0]
            # full_num = yearstr

    return_case = ""
    lookup_required = False
    imputed_salary = False

    final_salary = 0

    #Check current season 
    that_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == int(full_num))]

    ###CHECK AGAINST NULL LIST
    if(candidate_name in nulldb_name_list):
        
        #NULL NAME - NOT IN DB SEASON OF MATCH
        if(len(that_season_that_guy) == 0):
            prev_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == (int(full_num) + 1))]
            next_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == (int(full_num) - 1))]
            thatguy_3seasons = pd.concat([that_season_that_guy, prev_season_that_guy, next_season_that_guy], ignore_index=True)
            
            #NOT IN DB FOR YEAR BEFORE OR AFTER THE MATCH
            if(len(thatguy_3seasons) == 0):
                #print(f'{candidate_name} wasn\'t in the db in {full_num}, {int(full_num) + 1} or {int(full_num) - 1} ')

                ###AAA
                return_case = "not in DB any of 3 seasons."
                lookup_required = True
            else:

                ####how do we make sure this guy was really the guy??? 
                ####ZZZZ   
                print(f'{candidate_name} was not in the db in {full_num}, but was in {int(full_num) + 1} or {int(full_num) - 1} ')
                lookup_required = True
                return_case = "was in DB in before or after season"
            
        else:
        ###IMPUTE CASE 1###
        #NULL NAME, BUT THEY WERE IN THE DB THE SEASON OF THE MATCH
            # league = that_season_that_guy.reset_index().at[0, 'League']
            # season = that_season_that_guy.reset_index().at[0, 'Season']
            # age = that_season_that_guy.reset_index().at[0, 'Age']
            # mean_salary_values = pd.to_numeric(database_name[(database_name['League'] == league) & (database_name['Season'] == season) & (database_name['Age'] == age)][f'{money_column_name}'])
            # meansalary = mean_salary_values.mean()
            # final_salary = meansalary

            #print(f"For {candidate_name}, imputed salary of {meansalary} using {league}, {season} season and age {age}")
            
            ####IS THERE ANY WAY THIS GUY IS NOT THE GUY?
            # imputed_salary = True
            # return_case = "working - imputed"

            lookup_required = True
            return_case = "was in DB in before or after season"
    else:
        #NON-NULL NAME

        #NO ROWS FOR YEAR OF THE MATCH
        if(len(that_season_that_guy) == 0):
            #print('were in here this time')

            #check season prior and following 
            prev_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == (int(full_num) + 1))]
            next_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == (int(full_num) - 1))]
            thatguy_3seasons = pd.concat([that_season_that_guy, prev_season_that_guy, next_season_that_guy], ignore_index=True)
            
            print(int(full_num) + 1, int(full_num) - 1)
            #NO DATA FOR YEAR BEFORE OR AFTER THE MATCH
            if(len(thatguy_3seasons) == 0):
                #print(f'{candidate_name} wasn\'t in the db in {full_num}, {int(full_num) + 1} or {int(full_num) - 1} ')
                ###AAA
                return_case = "player not in DB any of 3 seasons."
                lookup_required = True
                #print(f'3season length is 0')
            #SOME DATA IN THE YEAR BEFORE OR AFTER THE MATCH
            else:
                ####how do we make sure this guy was really the guy???
                ####ZZZZ  
                #print(f'{candidate_name} was not in the db in {full_num}, but was in {int(full_num) + 1} or {int(full_num) - 1} ')
                lookup_required = True
                return_case = "asswipe was in DB in before or after season"
                
                
        
        #SOME ROWS FOR YEAR OF THE MATCH
        else:
            #print(f"{candidate_name} is in dataset for {int(full_num)}")

            #THEIR SALARY OR VALUE THAT SEASON
            array_with_nan = that_season_that_guy[f'{money_column_name}'].unique()
            
            numeric_values = pd.to_numeric(array_with_nan, errors='coerce')

            #CURRENT SEASON IS NULL DATA
            if np.isnan(numeric_values).all():
                print('chilly1')
                #print("1 season: All-NaN slice encountered")
                #USING THEIR OWN SALARIES FROM SZN BEFORE / AFTER
                prev_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == (int(full_num) + 1))]
                next_season_that_guy = database_name[(database_name['Name'] == candidate_name) & (database_name['Season'] == (int(full_num) - 1))]
                thatguy_3seasons = pd.concat([that_season_that_guy, prev_season_that_guy, next_season_that_guy], ignore_index=True)
                
                szn_array_with_nan = thatguy_3seasons[f'{money_column_name}'].unique()
                numeric_values_3szn = pd.to_numeric(szn_array_with_nan, errors='coerce')

                #PREV / FOLLOWING SEASON IS NULL DATA
                if np.isnan(numeric_values_3szn).all():
                    print(f'{(int(full_num) + 1)}, {(int(full_num) -1)}, chilly2')

                    #print("3 seasons: All-NaN slice encountered")
                    ###IMPUTE CASE 2###

                    #USING LEAGUE AVG SALARIES
                    # league = that_season_that_guy.reset_index().at[0, 'League']
                    # season = that_season_that_guy.reset_index().at[0, 'Season']
                    # age = that_season_that_guy.reset_index().at[0, 'Age']
                    # mean_salary_values = pd.to_numeric(database_name[(database_name['League'] == league) & (database_name['Season'] == season) & (database_name['Age'] == age)][f'{money_column_name}'])
                    # meansalary = mean_salary_values.mean()
                    # final_salary = meansalary

                    #print(f"For {candidate_name}, imputed salary of {meansalary} using {league}, {season} season and age {age}")
                    #imputed_salary = True
                    #return_case = "working - imputed"
                    lookup_required = True
                    return_case = "was in DB in before or after season"
                    
                else:
                    #There are salaries in the 3 season dataset
                    print(f'for {candidate_name}, {money_column_name} info is not in {int(full_num)} but IS in {int(full_num) + 1} or {int(full_num) - 1}')
                    ####ZZZZ
                    lookup_required = True
                    return_case = "was in DB in before or after season"

            else:
                # Find the maximum value excluding NaNs
                max_value_excluding_nan = np.nanmax(numeric_values)
                final_salary = max_value_excluding_nan
                #print(f"{money_column_name} in {input_year_test} is {max_value_excluding_nan}")
                return_case = "working"

    return final_salary, return_case, lookup_required, imputed_salary

# %%
def fourth_try_name_search(input_search_name, input_nationality, using_salaries_boolean):


    if(using_salaries_boolean == True): #salaries_or_values == "salary"
        database_name = leagues_salary
        #money_column_name = "Inflation-Adjusted Yearly Salary"
    elif(using_salaries_boolean == False): #salaries_or_values == "value"
        database_name = leagues_value_large

    fourthsearch_name = ""
    match_type = ""
    fourthsearch_list = []

    search_name = input_search_name
    natl_test = input_nationality
    #search_name = name_match[2]
    result = filter_names_first_initial_lastname(database_name['Name'].unique(), search_name)
    list_left = filter_candidates(search_name, result)

    natl_list = []
    for i in range(0, len(list_left)):
        if(natl_test in database_name[database_name['Name'] == list_left[i]]['Nationality'].unique()):
            natl_list.append(list_left[i])

    if(len(natl_list) == 1):
        
        #one match remaining. 
        #RETURN
        #print(f'after filtering 4th time found {natl_list[0]}')

        fourthsearch_name = natl_list[0]
        match_type = 'single'
        

    elif(len(natl_list) >= 2):
        #still not quite matched up
        #print something. probably should search this guy as part of 
        
        match_type = 'multiple'
        fourthsearch_list = natl_list
    else:
        match_type = 'none'
        #print(f'no match after 4: {search_name}')

    if(match_type == 'single'):
        return match_type, fourthsearch_name 
    elif(match_type == 'multiple'):
        return match_type, fourthsearch_list 
    else:
        #no match
        #print(f'no match found: {search_name}')
        return match_type, search_name

# %%
def filter_candidates_using_year(starter_number, input_list_of_names, input_nationality, input_match_date, using_salaries_boolean):

    list_of_names = input_list_of_names
    natl_test = input_nationality
    input_year_test = input_match_date

    if(using_salaries_boolean == True): #salaries_or_values == "salary"
        database_name = leagues_salary
        #money_column_name = "Inflation-Adjusted Yearly Salary"
    elif(using_salaries_boolean == False): #salaries_or_values == "value"
        database_name = leagues_value_large
        #money_column_name = "Market Value"

    if '.' in input_year_test:
        yearstr = input_year_test.split(".")[2]
        full_num = int('20' + yearstr)
    elif '-' in input_year_test:
        if len(input_year_test.split("-")[2]) == 4:
            yearstr = input_year_test.split("-")[2] #this is a 4 digit number
            full_num = int(yearstr)
        elif len(input_year_test.split("-")[2]) == 2:
            if len(input_year_test.split("-")[0]) == 4:
                yearstr = input_year_test.split("-")[0]
                full_num = int(yearstr)
            else:
                yearstr = input_year_test.split("-")[2] #this is a 2 digit number
                full_num = int('20' + yearstr)
        else:
            print('broke on year parsing', input_year_test.split("-"))
        
    season_num = int(full_num)
    #print('season we look for is ', season_num)

    result_name_array = list()
    for i in range(0, len(list_of_names)):
        this_name = list_of_names[i]
        

        checking_name_subset = database_name[(database_name['Name'] == this_name) & (database_name['Nationality'] == natl_test) & (database_name['Season'] == season_num)]
        
        if ((starter_number != 1) & ('Goalkeeper' in checking_name_subset['Position'].unique())):
            0==0
            
        else:
            if(len(checking_name_subset) >= 1):
                result_name_array.append(this_name)  

    return result_name_array


# %% [markdown]
# ##### Common last name case functions - find correct name using Transfermarkt International History
# 
# Lovren

# %%
def process_date_format_for_transfermarkt_lookup(input_date):
    try:
        # Try to parse the input date in different formats
        date_formats = ["%Y-%m-%d", "%m.%d.%y", "%d-%m-%Y", "%d-%b-%y", "%d.%m.%y"]
        parsed_date = None
        for format_str in date_formats:
            try:
                parsed_date = datetime.strptime(input_date, format_str)

                # If parsing is successful, break out of the loop
                break
            except ValueError:
                continue

        # If parsing is successful, format the date in MM-DD-YY
        if parsed_date:
            output_date = parsed_date.strftime("%m/%d/%y")
            return output_date
        else:
            return "Invalid date format"
    except Exception as e:
        return str(e)

# Example usage:
# case 1 - YYYY-MM-DD
#input_date = "2022-01-22"
# case 2 - DD.MM.YY
#input_date = "08.06.19"
#case 3 - DD-MM-YYYY
#input_date = "29-03-2017"
#case 4 - DD-MMM-YY (text)
#input_date = "05-Jun-21"
#output_date = process_date_format_for_transfermarkt_lookup(input_date)
#print(output_date)


# %%
def transform_name(name):
    # Remove apostrophes or backticks
    name_without_apostrophe = name.replace("'", "").replace("`", "")

    # Replace spaces with dashes and convert to lowercase
    transformed_name = '-'.join(name_without_apostrophe.split()).lower()

    return transformed_name

# %%
def grab_transfer_pagesoup(input_url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    pageTree = requests.get (input_url, headers = headers)
    pageSoup_club = BeautifulSoup (pageTree.content, 'html.parser')
    
    return pageSoup_club

# %%
def add_leading_zeros(date_str):
    components = date_str.split('/')
    components = [component.zfill(2) if len(component) == 1 else component for component in components]
    return '/'.join(components)

# %%
def find_transfermarkt_pagesoup_player(input_playername, input_nationality_string):
    #search = f"{vet_for_match_season[1]} Transfermarkt"
    search = f"{input_playername} Transfermarkt {input_nationality_string} National Team"
    

    #print('find_transfermarkt_pagesoup_player. search was', search)
    url = 'https://www.google.com/search'

    headers = {'Accept' : '*/*', 'Accept-Language': 'en-US,en;q=0.5','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers = headers, params = parameters).text
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id = 'search')
    first_link = search.find('a')
    #print(str(first_link), 'href' in str(first_link))#['href']

    if 'href' in str(first_link):
        url_tosplit = (first_link['href'])
        #print(f"transfermarkt in. first URL is {url_tosplit}")
    else:
        #print('first link didn\'t work')
        all_links = soup.find_all('a')
        
        for link in all_links:
            href = link.get('href')
            if href and 'transfermarkt' in href:
                #print(href)
                url_tosplit = href
                break  # Exit the loop after printing the first matching link
            else:
                0==0
                #print('no href with', link)
    

    print(url_tosplit)
    player_name_string = url_tosplit.split('/')[3]
    player_code = url_tosplit.split('/')[6]

    find_national_team_history_URL = f"https://www.transfermarkt.us/{player_name_string}/nationalmannschaft/spieler/{player_code}"

    #print(f"this player is {input_playername}, URL is {find_national_team_history_URL}. lowercase is {input_playername.lower()}. transformed with my new change it's {transform_name(unidecode(input_playername.lower()))}")

    if((input_playername.lower() in find_national_team_history_URL) or (input_playername.lower() in find_national_team_history_URL) or (transform_name(input_playername.lower()) in find_national_team_history_URL) or (transform_name(unidecode(input_playername.lower())) in find_national_team_history_URL)):
        page_soup_history_pg = grab_transfer_pagesoup(find_national_team_history_URL)
    else:
        page_soup_history_pg = None
    
    return page_soup_history_pg

# %%
def find_national_team_in_player_history(pagesoup_input, nationality_input):

    page_soup_history_pg = pagesoup_input

    try:
        # FINDING THE NATIONAL TEAMS THEY PLAYED FOR 
        boxes = page_soup_history_pg.find_all("div", {"class": "box"})
        nationalteamcareer_table = boxes[0].find("table")
    except (IndexError, AttributeError):
        # Handle errors if the table is not found or an attribute is missing
        return False

    nationalteamcareer_table = boxes[0].find("table")

    rows = nationalteamcareer_table.find_all('tr')

    teams_played_for_array = []

    for i in range(0, len(rows)): 
        if(i == 0):
            0==0
        elif(i % 2 != 0):
            0==0
        else:
            this_row =  rows[i]

            nat_team_name = this_row.find_all("td", {"class": "hauptlink no-border-links hide-for-small"})[0].text.strip().encode().decode("utf-8")
            teams_played_for_array.append(nat_team_name)

    if nationality_input in teams_played_for_array:
        return True 
    else:
        return False

# %%
def find_match_date_in_player_history(input_date, pagesoup_input):
    #print(f'finding match date with {input_date} and {pagesoup_input}')
    date_found = False

    correctly_formatted_date = process_date_format_for_transfermarkt_lookup(input_date)
    print('correct format date is ', correctly_formatted_date)
    

    # Convert the correctly_formatted_date to datetime object
    correct_date_obj = datetime.strptime(correctly_formatted_date, "%m/%d/%y")

    print('date obj is ', correct_date_obj)

    # if str(correct_date_obj).endswith('00:00:00'):
    #     print('yay', str(correct_date_obj).split('00:00:00')[0])
    #     correct_date_obj =  str(correct_date_obj).split(' 00:00:00')[0]
    #     if('-') in correct_date_obj:
    #         if(len(correct_date_obj.split('-')[0]) == 4):
    #             year = correct_date_obj.split('-')[0]
    #             correct_date_obj = f"{correct_date_obj.split('-')[1]}/{correct_date_obj.split('-')[2]}/{year[2:]}"
    #         else:
    #             0==0
    #     print('converted correct date obj to', correct_date_obj)

    # Define function to check if a date matches or is one day before/after the given date
    def check_date(match_date, correct_date_obj):
        if(type(correct_date_obj) == str):
            0==0
            # correct_date_obj = datetime.strptime(correct_date_obj, '%Y-%m-%d')
            # correct_date_obj = correct_date_obj.strftime('%m/%d/%y')
            # correct_date_obj = datetime.strptime(correct_date_obj, '%m/%d/%y')
        match_date_obj = datetime.strptime(match_date, "%m/%d/%y")
        #correct_date_obj = datetime.strptime(correct_date_obj, "%m/%d/%y")
        #print('comparing ', match_date_obj, correct_date_obj)
        if (match_date_obj == correct_date_obj or 
            match_date_obj == correct_date_obj + timedelta(days=1) or 
            match_date_obj == correct_date_obj - timedelta(days=1)):
            return True
        else:
            return False

    table_test = pagesoup_input.find_all("div", {"class": "responsive-table"})[1].find_all("tbody")[0]

    for i in range(0, len(table_test.find_all('tr'))):
        this_tr_row = table_test.find_all('tr')[i]
        data_row = this_tr_row.find_all("td", {"class": "zentriert"})

        if len(data_row) == 1:
            pass
        elif len(data_row) == 7:
            pass
        elif len(data_row) == 12:
            match_date_row = data_row[1].text.strip()
            #print('this is in the regular date loop', match_date_row, correct_date_obj)
            if check_date(match_date_row, correct_date_obj):
                print('it was him')
                date_found = True
                return True
        else:
            print(i, len(data_row))

    # If not found with the original date format, switch the date format and try again
    if not date_found:
        # if type(correct_date_obj) == str:
        #     correct_date_obj = datetime.strptime(correct_date_obj, "%d/%m/%y")
        #     print('converted it is ', correct_date_obj)
        #     switched_date = correct_date_obj.strftime("%d/%m/%y")
        #     #print('ya it was a str')
        #     #correct_date_obj = datetime.strptime(correct_date_obj, '%Y-%m-%d')
        #     #switched_date = correct_date_obj.strftime('%d/%m/%y')
        #     #print('type of switched date is ', type(switched_date))
        #     # parts = switched_date.split('/')
        #     # # Check if the first part begins with '0'
        #     # if parts[0].startswith('0'):
        #     #     parts[0] = parts[0][1:]

        #     # # Check if the second part begins with '0'
        #     # if parts[1].startswith('0'):
        #     #     parts[1] = parts[1][1:]

        #     # # Reconstruct the date string
        #     # switched_date = '/'.join(parts)
        # else:
        #print('switching the day and month does this: ' , correct_date_obj.strftime("%d/%m/%y"))
        #switched_date = datetime.strptime(correct_date_obj.strftime("%d/%m/%y"), "%d/%m/%y")
        try: 
            switched_date = datetime.strptime(datetime.strftime(correct_date_obj, "%d/%m/%y"), "%m/%d/%y")
            print('switched date is ', switched_date)
            for i in range(0, len(table_test.find_all('tr'))):
                this_tr_row = table_test.find_all('tr')[i]
                data_row = this_tr_row.find_all("td", {"class": "zentriert"})
                if len(data_row) == 1:
                    pass
                elif len(data_row) == 7:
                    pass
                elif len(data_row) == 12:
                    match_date_row = data_row[1].text.strip()
                    #print('this is in the switched date loop', type(match_date_row), match_date_row, switched_date) #datetime.strptime(switched_date, "%m/%d/%y")
                    if check_date(match_date_row, switched_date): #datetime.strptime(switched_date, "%d/%m/%y")
                        date_found = True
                        return True
                    elif check_date(match_date_row, switched_date):
                        print('worked with ', match_date_row)
                        date_found = True
                        return True
                else:
                    print(i, len(data_row))
        except ValueError as ve:
            print("Error:", ve)


    if(date_found == False):
        return False


# %%
def find_transfermarkt_INFO_player(input_playername):
    #search = f"{vet_for_match_season[1]} Transfermarkt"
    search = f"{input_playername} Transfermarkt"


    url = 'https://www.google.com/search'

    headers = {'Accept' : '*/*', 'Accept-Language': 'en-US,en;q=0.5','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers = headers, params = parameters).text
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id = 'search')
    first_link = search.find('a')

    url_tosplit = (first_link['href'])

    player_name_string = url_tosplit.split('/')[3]
    player_code = url_tosplit.split('/')[6]

    find_value_history_URL = f"https://www.transfermarkt.us/{player_name_string}/marktwertverlauf/spieler/{player_code}"

    
    return find_value_history_URL

# %%
def multiNameMatchDateLookup(input_list_of_names, input_nationality, input_year_of_match):
    list_vetted_for_match_season = input_list_of_names
    natl_test = input_nationality
    input_year_test = input_year_of_match

    playernames_testing = list_vetted_for_match_season
    datematch_required = False
    result_array_aftertest = []
    players_pagesoup_dictionary = {}
    
    

    #print('list inside function is ', list_vetted_for_match_season)
    #print('inside function match date is ', input_year_test)

    for j in range(0, len(playernames_testing)):
        currplayer = playernames_testing[j]
        #print(f'multiNameMatchDateLookup. about to find page soup. were doing {currplayer}')
        transfermarkt_page_soup = find_transfermarkt_pagesoup_player(currplayer, natl_test)

        #print('this player is ', currplayer, transfermarkt_page_soup, natl_test)
        if(find_national_team_in_player_history(transfermarkt_page_soup, natl_test) == True):
            result_array_aftertest.append(currplayer)
            players_pagesoup_dictionary[currplayer] = transfermarkt_page_soup

    #print('multiNameMatchDateLookup. after findign natl team history list is ',result_array_aftertest)

    if(len(result_array_aftertest) == 1):
        #After this leg there's one match 
        candidate_name_r6 = result_array_aftertest[0]
        #money_thisplayer = find_money_info_from_name(candidate_name_r6, natl_test, input_year_test, salary_boolean)
        return candidate_name_r6
        
    elif((len(playernames_testing) == len(result_array_aftertest)) | (len(result_array_aftertest) >= 2)):
        
        #still multiple players w the same name who played for the nat'l team  
        datematch_required = True
        second_array_test = []

        for k in range(0, len(result_array_aftertest)):
            
            currplayer_2 = result_array_aftertest[k]

            #print(f'looking at {currplayer_2} to find {input_year_test} in history')
            pagesoup_this_guy = players_pagesoup_dictionary[currplayer_2]

            print(f'inside loop searching. player is {currplayer_2}')

            if(find_match_date_in_player_history(input_year_test, pagesoup_this_guy) == True):
                second_array_test.append(currplayer_2)

    else:
        #RESULTS ARRAY AFTER TEST LENGTH IS 0
        0==0
        #print('error ', result_array_aftertest)
        return result_array_aftertest #128201

    #if there were two guys w the same last name who both played for the national team 
    #and we needed to make sure one of them played on that date 
    if(datematch_required == True):

        if(len(second_array_test) == 1):
            candidate_name_r6 = second_array_test[0]
            #money_thisplayer = find_money_info_from_name(candidate_name_r6, natl_test, input_year_test, salary_boolean)
            #stop that
            return candidate_name_r6

        else:
            if(len(second_array_test) >= 2):
                0==0
                return second_array_test #print(list_vetted_for_match_season, second_array_test)
            else:
                #LENGTH OF SECOND ARRAY IS ZERO
                0==0
                return second_array_test #128202

            
            
                

# %% [markdown]
# #### AAA Case functions

# %%
def false_name_match_lookup(input_name, input_nationality):
    name_match = ['', '', input_name]
    natl_test = input_nationality
    search = f"{name_match[2]} {natl_test} national team"

    url = 'https://www.google.com/search'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers=headers, params=parameters).text
    soup = BeautifulSoup(content, 'html.parser')
    search_results = soup.find_all('a')

    # Collect links from Wikipedia or Transfermarkt
    wiki_links = []
    transfermarkt_links = []

    for result in search_results:
        link = result.get('href')
        if link:
            if 'wikipedia.org' in link:
                wiki_links.append(link)
            elif 'transfermarkt' in link:
                transfermarkt_links.append(link)

    # Extract and clean names from Wikipedia links
    wiki_names = []
    for wiki_link in wiki_links:
        match = re.search(r'/wiki/([^/]+)$', wiki_link)
        if match:
            raw_name = match.group(1).replace('_', ' ')
            cleaned_name = re.sub(r'%27', "'", urllib.parse.unquote(raw_name))  # Handle %27 as an apostrophe
            cleaned_name = ' '.join([part.capitalize() for part in cleaned_name.split()])
            wiki_names.append(cleaned_name)

    # Extract and clean names from Transfermarkt links
    transfermarkt_names = []
    for tm_link in transfermarkt_links:
        parts = tm_link.split('/')
        if len(parts) >= 5 and parts[5] == 'spieler':
            raw_name = parts[3].replace('-', ' ')
            cleaned_name = ' '.join([part.capitalize() for part in raw_name.split()])
            transfermarkt_names.append(cleaned_name)

    # Get unique names for each website
    unique_wiki_names = set(wiki_names)
    unique_transfermarkt_names = set(transfermarkt_names)

    # Get unique names for each website
    unique_wiki_names = set(wiki_names)
    unique_transfermarkt_names = set(transfermarkt_names)

    # Combine unique names, accounting for variations
    combined_unique_names = set()

    for wiki_name in unique_wiki_names:
        for tm_name in unique_transfermarkt_names:
            # Normalize names by removing spaces, accents, and converting to lowercase
            normalized_wiki_name = re.sub(r'[^a-zA-Z0-9]', '', wiki_name.lower())
            normalized_tm_name = re.sub(r'[^a-zA-Z0-9]', '', tm_name.lower())

            # Check if normalized names match
            if normalized_wiki_name == normalized_tm_name:
                # Choose the name with apostrophes from Wikipedia list
                combined_unique_names.add(wiki_name)

    # Print or use the combined unique names
    # print("Combined Unique Names:")
    # for name in combined_unique_names:
    #     print(name)
    return combined_unique_names

# %% [markdown]
# #### SELENIUM Case Functions - VALUES

# %% [markdown]
# #### Helper Functions

# %% [markdown]
# ##### Ala addin mahdi case functions

# %%
def closest_match(candidate_name, possible_names):
    # Get closest matches using difflib
    matches = difflib.get_close_matches(candidate_name, possible_names)

    if matches:
        # Return the closest match
        return matches[0]
    else:
        # No close match found
        return None

def findNamesOnPageUsingSoup(input_beautifulsoup):

    search_results = input_beautifulsoup.find_all('a')

    transfermarkt_links = []

    for result in search_results:
        link = result.get('href')
        if link:
            if ('transfermarkt' in link) and ('spieler' in link):
                transfermarkt_links.append(link)

    #def extract_domain_substring(url):
    phrases = ['.us/', '.tr/', '.in/', '.com/', '.uk/', '.de/', '.fr/']

    #url = transfermarkt_links[3]


    #parsed_url = urlparse(url)
    #path = parsed_url.path

    names_in_links = []
    link_indexes = []
    original_links = []

    names_dataframe = pd.DataFrame()

    rows_counter = 0

    for i in range(0, len(transfermarkt_links)):
        url = transfermarkt_links[i]

        for phrase in phrases:
            if phrase in url:

                #print(i, url)
                #original_links.append(url)
                #link_indexes.append(i)
                start_index = url.find(phrase) + len(phrase)
                end_index = url.find('/', start_index)
                if end_index != -1:
                    correct_name_from_url = url[start_index:end_index]
                    #names_in_links.append(correct_name_from_url)
                    #print(i, correct_name_from_url)
                    new_row = {'Link': url, 'Name': correct_name_from_url}

                    new_row  = pd.DataFrame(new_row, index=[rows_counter])

                    # Add the new row to the DataFrame
                    names_dataframe = pd.concat([names_dataframe, new_row], ignore_index=True) 

                    rows_counter += 1
                    
                else:
                    print('2', url[start_index:])

    filtered_dataframe_names = names_dataframe[names_dataframe['Name'].apply(lambda x: bool(re.match("^[a-zA-Z-]+$", x)))].reset_index().drop(columns='index', axis=1)

    filtered_dataframe_names['Name'] = filtered_dataframe_names['Name'].apply(lambda x: x.replace('-', ' '))

    filtered_dataframe_names['Name'] = filtered_dataframe_names['Name'].apply(lambda x: x.title())

    for i in range(len(filtered_dataframe_names['Link'])):
        link = filtered_dataframe_names.at[i, 'Link']
        occurrences = link.count('https:')
        
        # If there are more than 1 "https:", keep only the part starting from the second occurrence
        if occurrences > 1:
            second_occurrence_index = link.find('https:', link.find('https:') + 1)
            filtered_dataframe_names.at[i, 'Link'] = link[second_occurrence_index:]

    return filtered_dataframe_names

# %% [markdown]
# #### Husain Ali Pele case functions

# %%
def is_valid_link(url):
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        
        # Open the URL with the headless browser
        driver.get(url)
        
        # Get the final URL after page load
        final_url = driver.current_url
        
        # Compare the original URL with the final URL
        return url == final_url
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        driver.quit()

def extract_information_from_link(link):
    # Define regular expressions for extracting information
    competition_regex = r'(?:\.com/|\.us/|\.tr/)([^/]+)'
    spieler_regex = r'spieler/([^/]+)'

    # Extract information using regular expressions
    competition_match = pd.Series(link).str.extract(competition_regex, expand=False).iloc[0]
    spieler_match = pd.Series(link).str.extract(spieler_regex, expand=False).iloc[0]

    return competition_match, spieler_match

def remove_row_by_link(dataframe, target_link):
    # Check if the target link exists in the 'Link' column
    index_to_remove = dataframe[dataframe['Link'] == target_link].index
    
    # Remove the row if the link is found
    if not index_to_remove.empty:
        dataframe = dataframe.drop(index_to_remove)
        #print(f"Row with link {target_link} removed.")
    else:
        print(f"Link {target_link} not found in the dataframe.")
    
    return dataframe

def filter_similar_names(target_name, names_array, threshold=0.6):
    reversed_target_name = ' '.join(reversed(target_name.split()))
    
    similar_names = [name for name in names_array if (
        Levenshtein.ratio(target_name.lower(), name.lower()) >= threshold
        or Levenshtein.ratio(reversed_target_name.lower(), name.lower()) >= threshold
    )]
    
    return similar_names

# %% [markdown]
# ##### Djeparov case functions

# %%
def is_trainer_url_not_player_url(url):
    # Check if "trainer" is in the URL
    condition1 = "trainer" in url.lower()

    # Check if "spieler" is not in the URL
    condition2 = "spieler" not in url.lower()

    # Return True if both conditions are met, otherwise False
    return condition1 and condition2

# %%
def process_date_format_for_market_value_table_lookup(input_date):
    try:
        # Try to parse the input date in different formats
        date_formats = ["%Y-%m-%d", "%d.%m.%y", "%d-%m-%Y", "%d-%b-%y"]
        parsed_date = None
        for format_str in date_formats:
            try:
                parsed_date = datetime.strptime(input_date, format_str)

                # If parsing is successful, break out of the loop
                break
            except ValueError:
                continue

        # If parsing is successful, format the date in YYYY-MM-DD
        if parsed_date:
            output_date = parsed_date.strftime("%Y-%m-%d")
            return output_date
        else:
            return "Invalid date format"
    except Exception as e:
        return str(e)

# Example usage:
# case 1 - YYYY-MM-DD
#input_date = "2022-01-22"

# case 2 - DD.MM.YY
#input_date = "03.09.15"

# case 3 - DD-MM-YYYY
#input_date = "03-09-2015"

# case 4 - DD-MMM-YY
#input_date = "03-Sep-15"

#output_date = process_date_format_for_market_value_table_lookup(input_date)
#print(output_date)

# %% [markdown]
# #### Mahmoud abu warda cases

# %%
def parse_date(entry_date):
    has_month = False  # Initialize the boolean variable

    try:
        # Try to parse as 'Sep 22' format
        date_obj = datetime.strptime(entry_date, '%b %y')
        year = date_obj.strftime('%y')
        month = date_obj.strftime('%b')
        has_month = True  # Set to True if parsing succeeds
    except ValueError:
        try:
            # Try to parse as 'MAR 2021' format
            date_obj = datetime.strptime(entry_date, '%b %Y')
            year = date_obj.strftime('%y')
            month = date_obj.strftime('%b')
            has_month = True  # Set to True if parsing succeeds
        except ValueError:
            # If parsing fails, assume it's just a year like '2017'
            try:
                date_obj = datetime.strptime(entry_date, '%Y')
                year = date_obj.strftime('%y')
                month = 'Dec'  # Default month if only year is provided
            except ValueError:
                # If it's neither of the formats, handle accordingly
                year = None
                month = None

    return year, month, has_month

#parse_date('Sep 2021')

# %%
def getSeleniumURL(input_name_for_lookup, input_nationality, input_date_of_match):

    search = f'{input_name_for_lookup} {input_nationality} transfermarkt' #replace this

    url = 'https://www.google.com/search'

    headers = {'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82'}

    parameters = {'q': search}

    content = requests.get(url, headers=headers, params=parameters).text
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id='search')
    first_link = search.find('a')

    url_tosplit = first_link['href']

    # Use urlsplit to extract the domain
    parsed_url = urlsplit(url_tosplit)

    link_invalid_bool = False

    if parsed_url.netloc == 'www.transfermarkt.us' or parsed_url.netloc == "www.transfermarkt.com":

        #print('1')
        ###CHECK IF URL IS VALID HERE###
        ###IF NOT DO SOMETHING ELSE
        ###IF YES JUST RETURN IT
        if is_valid_link(url_tosplit):
            print("The link is valid.")
            if(is_trainer_url_not_player_url(first_link['href']) == True):
            #URL IS A MANAGER URL
                print('this is a manager URL', url_tosplit)
                
                search = f'{input_name_for_lookup} {input_nationality} spieler transfermarkt' #replace this

                url = 'https://www.google.com/search'

                headers = {'Accept': '*/*', 'Accept-Language': 'en-US,en;q=0.5', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82'}

                parameters = {'q': search}

                content = requests.get(url, headers=headers, params=parameters).text
                soup = BeautifulSoup(content, 'html.parser')

                search = soup.find(id='search')
                first_link = search.find('a')

                url_tosplit = first_link['href']
                if is_valid_link(url_tosplit):
                    print("The link is valid.")
                    link_invalid_bool = True
                    url_is_transfermarkt = True
                    name_for_final_url = url_tosplit.split('/')[3]
                    code_for_final_url = url_tosplit.split('/')[6]
                    url_tosplit = f"https://www.transfermarkt.us/{name_for_final_url}/marktwertverlauf/spieler/{code_for_final_url}"
                else:
                    print("The link is not valid.")
                    url_tosplit = ""


            else:
                #URL IS A PLAYER URL
                url_is_transfermarkt = True
                link_invalid_bool = True

                name_for_final_url = url_tosplit.split('/')[3]
                code_for_final_url = url_tosplit.split('/')[6]
                url_tosplit = f"https://www.transfermarkt.us/{name_for_final_url}/marktwertverlauf/spieler/{code_for_final_url}"
                #print('yes')
        else:
            print("The link is not valid.")
            url_tosplit = ""
            
        
    else:
        
        url_is_transfermarkt = False #may need to comment this out 
        print(f'link not from transfermarkt. link is from {parsed_url.netloc}')

        names_on_page = findNamesOnPageUsingSoup(soup)
        all_names = set(names_on_page['Name'])
        candidate_name_links_search = input_name_for_lookup 

        closest_match_result = closest_match(candidate_name_links_search, all_names)

        if(closest_match_result == None):
            print('no closest match result for:', input_name_for_lookup, 'this is in getSeleniumURL') 
            ###IMPUTE CASE 3### SPECIFIC TO VALUES
            #DOES THIS JUST RETURN THO? MAYBE YOU TAKE CARE OF IT LATER 
        else:
            #print(closest_match_result)

            dataframe_filtered = names_on_page[names_on_page['Name'] == closest_match_result].reset_index()

            url_is_transfermarkt = True

            correct_link_for_name = dataframe_filtered.at[0, 'Link']
            print('2')
            if is_valid_link(correct_link_for_name):
                print("The link is valid.")
                name_for_final_url = correct_link_for_name.split('/')[3]
                code_for_final_url = correct_link_for_name.split('/')[6]
                url_tosplit = f"https://www.transfermarkt.us/{name_for_final_url}/marktwertverlauf/spieler/{code_for_final_url}" 
                link_invalid_bool = True
            else:
                print("The link is not valid.")
                url_tosplit = ""
                #link_invalid_bool = True

    if(link_invalid_bool == False):
        names_on_page = findNamesOnPageUsingSoup(soup)
        df = remove_row_by_link(names_on_page, first_link['href']).reset_index().drop(columns='index', axis=1)
        df[['Name URL style', 'Spieler']] = df['Link'].apply(extract_information_from_link).apply(pd.Series)

        df = df.drop_duplicates(subset=['Name URL style', 'Spieler'], keep='first').reset_index().drop(columns='index', axis=1)

        result_array_aftertest = []
        players_pagesoup_dictionary = {}

        for i in range(0, len(df)):
            this_url_name = df.at[i, 'Name URL style']
            this_code_name = df.at[i, 'Spieler']
            find_national_team_history_URL = f"https://www.transfermarkt.us/{this_url_name}/nationalmannschaft/spieler/{this_code_name}"

            print(df.at[i, 'Name'], find_national_team_history_URL)

            page_soup_history_pg = grab_transfer_pagesoup(find_national_team_history_URL)

            if(find_national_team_in_player_history(page_soup_history_pg, input_nationality) == True):
                result_array_aftertest.append(df.at[i, 'Name'])
                players_pagesoup_dictionary[df.at[i, 'Name']] = page_soup_history_pg


        #need to get the page soup from a guy (national page), then you can run it 

        #get the page soup
        filtered_names = filter_similar_names(input_name_for_lookup, result_array_aftertest)
        #for each of these remaining names

        #loop through the dictionary that you made 
        #use the names as keys to get their page soup 
        #do the "find match date in history" function with the page_soup_history_pg and the input_year_test

        date_match_array_players = []

        for i in range(0, len(filtered_names)):
            #print(filtered_names[i], players_pagesoup_dictionary[filtered_names[i]])
            if(find_match_date_in_player_history(input_date_of_match, players_pagesoup_dictionary[filtered_names[i]]) == True):
                print('true', filtered_names[i])
                ###when it works###
                date_match_array_players.append(filtered_names[i])
            else:
                print('false', filtered_names[i])
                

        if(len(date_match_array_players) == 1):
            candidate_name_r6 = date_match_array_players[0]
            print('match found. you never finished this!!')
            #you have to return this guy's profile URL 

        elif(len(date_match_array_players) >= 2):
            print('multiple matches', date_match_array_players)
        else:
            print('0 matches', filtered_names)
            url_tosplit = ""
            url_is_transfermarkt = False
            ###IMPUTE CASE 4 ### SPECIFIC TO VALUES
            #wtf is going on here 
    else:
        0==0

    return url_tosplit, url_is_transfermarkt

def new_seleniumFindMarketValueGraph(input_history_URL, max_retries=5):
    #max_retries = 5
    for retry in range(max_retries):
        service = Service()
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)

        try:
            ID = "id"
            NAME = "name"
            XPATH = "xpath"
            LINK_TEXT = "link text"
            PARTIAL_LINK_TEXT = "partial link text"
            TAG_NAME = "tag name"
            CLASS_NAME = "class name"
            CSS_SELECTOR = "css selector"

            driver.get(input_history_URL)

            elements = driver.find_elements(By.XPATH, '/html/body/div/main/div[3]/div[1]/div/tm-market-value-development-graph-extended/div/div')

            # Check if elements were found
            if elements:
                # Access the first element in the list
                first_element = elements[0]

                # Get the text content of the element
                element_text = first_element.text
                #print(f"Text Content: {element_text}")

                # Alternatively, get the outer HTML of the element
                element_html = first_element.get_attribute('outerHTML')

                if element_html == '<div class="content-box-headline">Loading...</div>':
                    print("Retrying...")
                    raise ValueError("Loading... message detected")

            else:
                elements = driver.find_elements(By.XPATH, '/html/body/div/main/div[2]/div[1]/div/tm-market-value-development-graph-extended/div/div')
                if elements:
                    # Access the first element in the list
                    first_element = elements[0]

                    # Get the text content of the element
                    element_text = first_element.text
                    #print(f"Text Content: {element_text}")

                    # Alternatively, get the outer HTML of the element
                    element_html = first_element.get_attribute('outerHTML')

                    if element_html == '<div class="content-box-headline">Loading...</div>':
                        print("Retrying...")
                        raise ValueError("Loading... message detected")

                else:
                    print('nayem case')
                    element_html = ""

        except ValueError as e:
            print(e)
            driver.quit()
            continue
        else:
            # Close the WebDriver if successful
            driver.quit()
            if len(element_html) == 0:
                # It didn't return anything
                return ""
            else:
                # print(f"Outer HTML: {element_html}")
                return element_html

    # If max retries reached and still not successful, return an empty string
    return ""

def OLDER_PRE_JAN_25_seleniumFindMarketValueGraph (input_history_URL):
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    ID = "id"
    NAME = "name"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"

    driver.get(input_history_URL)

    elements = driver.find_elements(By.XPATH, '/html/body/div/main/div[3]/div[1]/div/tm-market-value-development-graph-extended/div/div')

    # Check if elements were found
    if elements:
        # Access the first element in the list
        first_element = elements[0]

        # Get the text content of the element
        element_text = first_element.text
        print(f"Text Content: {element_text}")

        # Alternatively, get the outer HTML of the element
        element_html = first_element.get_attribute('outerHTML')
    else:
        #print('2nd attempt')
        elements = driver.find_elements(By.XPATH, '/html/body/div/main/div[2]/div[1]/div/tm-market-value-development-graph-extended/div/div')
        if elements:
            # Access the first element in the list
            first_element = elements[0]

            # Get the text content of the element
            element_text = first_element.text
            print(f"Text Content: {element_text}")

            # Alternatively, get the outer HTML of the element
            element_html = first_element.get_attribute('outerHTML')
        else:
            print('nayem case')
            element_html = ""

    # Close the WebDriver
    driver.quit()

    if(len(element_html) == 0):
        #it didn't return anything
        return ""
    else:
        #print(f"Outer HTML: {element_html}")
        return element_html

def extract_axis_points(outer_html):
    soup = BeautifulSoup(outer_html, 'html.parser')

    # Extract X axis points
    x_axis_points = []
    x_axis_elements = soup.select('.axis.svelte-oklk3z text')
    
    # Add the origin point
    x_axis_points.append({'value': '0', 'coordinates': (0, 320)})

    # Extract other X axis points
    for i, element in enumerate(x_axis_elements):
        value = element.get_text().strip()
        transform_attribute = element.find_parent('g')['transform']
        x_coordinate = float(transform_attribute.split('(')[1].split(',')[0])
        y_coordinate = float(transform_attribute.split(',')[1].split(')')[0])
        x_axis_points.append({'value': value, 'coordinates': (x_coordinate, y_coordinate)})

    # Adjust the last X axis point
    #x_axis_points[-1]['coordinates'] = (0, 42.727272727272734)

    # Calculate coordinates for other X axis points
    # x_interval = 55.4545454545
    # for i in range(len(x_axis_points) - 2, 0, -1):
    #     x_axis_points[i]['coordinates'] = (0, x_axis_points[i+1]['coordinates'][1] + x_interval)

    # Extract Y axis points
    y_axis_points = []
    y_axis_elements = soup.select('.axis.svelte-3ta12v text')
    for element in y_axis_elements:
        value = element.get_text().strip()
        transform_attribute = element.find_parent('g')['transform']
        x_coordinate = float(transform_attribute.split('(')[1].split(',')[0])
        y_coordinate = float(transform_attribute.split(',')[1].split(')')[0])
        y_axis_points.append({'value': value, 'coordinates': (x_coordinate, y_coordinate)})
    
    ###Y AXIS THING TO COMMENT OUT###
    #y_axis_points.append({'value': 2023, 'coordinates': (701.634619143, 0.0)})

    if str(x_axis_points[-1]['coordinates'][1]).startswith('88'):
        #print("The value starts with '88'")
        for i in range(0, len(x_axis_points)):
            differencearray = []
            if(i != 0):
                currnumber = x_axis_points[i]['coordinates'][1]
                prevnumber = x_axis_points[i-1]['coordinates'][1]
                difference = prevnumber - currnumber
                differencearray.append(difference)
                #print(i, currnumber, difference)

        coordinate_tickmark_difference = np.average(differencearray)

        x_axis_points.append({'value': '0', 'coordinates': (0, x_axis_points[-1]['coordinates'][1] - coordinate_tickmark_difference)})


    return x_axis_points, y_axis_points

def extract_data_points(html):
    soup = BeautifulSoup(html, 'html.parser')
    data_points = soup.select('image')

    result = []
    for i, data_point in enumerate(data_points, start=1):
        x = float(data_point['x'])
        y = float(data_point['y'])
        result.append(f"Point {i}: x= {x}, y= {y}")

    return result

def create_x_points_dataframe(data):
    # Create lists to store data
    x_list, y_list, value_list = [], [], []

    # Iterate through data and fill lists
    for entry in data:
        x, y = entry['coordinates']
        value = entry['value']

        # Convert value to numeric format
        if value.endswith(('k', 'K')):
            value = float(value[:-1]) * 1000
        elif value.endswith(('m', 'M')):
            value = float(value[:-1]) * 1000000
        else:
            value = float(value)

        # Append to lists
        x_list.append(x)
        y_list.append(y)
        value_list.append(int(value))

    # Create DataFrame
    df = pd.DataFrame({'X': x_list, 'Y': y_list, 'Value': value_list})

    
    row_value_difference_array = []
    if(df.iloc[len(df) - 1]['Value'] == 0):
        #print('yes', df)
        for i in range(len(df)):
            this_row_value = df.at[i, 'Value']
            if(i == len(df) - 1):
                0==0
            elif(i != 0):
                difference_row_to_previous = this_row_value - df.at[i-1, 'Value']
                row_value_difference_array.append(difference_row_to_previous)

        value_difference_between_rows = np.average(row_value_difference_array)
        
        df.at[len(df)-1, 'Value'] = df.at[len(df)-2, 'Value'] + value_difference_between_rows

    return df

def create_y_points_dataframe(data):
    # Create lists to store data
    x_list, y_list, date_list = [], [], []

    # Iterate through data and fill lists
    for entry in data:
        x, y = entry['coordinates']
        x_list.append(x)
        y_list.append(y)
        # Example usage:
        year, month, has_month = parse_date(entry['value'])

        if(has_month):
            last_day = calendar.monthrange(int(f'20{year}'), list(calendar.month_abbr).index(month))[1]

            
            date_str_withmonth = f"{month} {last_day}, {int(year):02d}"
            date_month_included = datetime.strptime(date_str_withmonth, "%b %d, %y")
            #print(date_month_included)
            date_list.append(date_month_included)
        else:
            print(entry, year)
            date_str = f"Dec 31, {int(year):02d}"
            date = datetime.strptime(date_str, "%b %d, %y")
            
            date_list.append(date)

    # Create DataFrame
    df = pd.DataFrame({'X': x_list, 'Y': y_list, 'Date': date_list})

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    ###UNFORESEEN 4###
    result = calculate_differences_date_X_coordinate(df)

    last_row_length = df.at[len(df)-1, 'X'] + result[0]

    original_timestamp = df.at[len(df)-1, 'Date']
    days_to_add = result[1] 

    new_timestamp = original_timestamp + pd.to_timedelta(days_to_add, unit='D')

    # New row data
    new_row = {'X': last_row_length, 'Y': 0, 'Date': new_timestamp}

    new_row  = pd.DataFrame(new_row, index=[len(df)])

    # Add the new row to the DataFrame
    df = pd.concat([df, new_row], ignore_index=True)  

    return df

def create_data_points_table(data):
    # Create lists to store data
    point_list, x_list, y_list, market_value_list, date_list = [], [], [], [], []

    # Iterate through data and fill lists
    for entry in data:
        # Extract point number
        point_number = int(entry.split(':')[0].split()[-1])

        # Extract x and y coordinates
        x_coordinate = float(entry.split('x= ')[1].split(',')[0])
        y_coordinate = float(entry.split('y= ')[1])

        # Append to lists
        point_list.append(point_number)
        x_list.append(x_coordinate)
        y_list.append(y_coordinate)
        #market_value_list.append(0)  # Default market value
        market_value_list.append(np.float64(0))
        date_list.append(datetime(2000, 1, 1))  # Default date

    # Create DataFrame
    df = pd.DataFrame({
        'Point': point_list,
        'X': x_list,
        'Y': y_list,
        'Market Value': market_value_list,
        'Date': date_list
    })

    return df

def calculate_differences_date_X_coordinate(input_df):
    # Convert the 'Date' column to datetime type
    input_df['Date'] = pd.to_datetime(input_df['Date'])
    
    # Calculate the difference in 'X' column
    x_differences = input_df['X'].diff().mean()
    
    # Calculate the difference in 'Date' column
    date_differences = (input_df['Date'].diff().mean()).days
    
    return x_differences, date_differences

def estimate_value(input_y_mv, x_points_dataframe):
    # Find the two closest Y values in the DataFrame
    closest_y_values = x_points_dataframe['Y'].nsmallest(2)
    
    # Extract the corresponding values and Y coordinates
    value1 = x_points_dataframe.loc[x_points_dataframe['Y'] == closest_y_values.iloc[0], 'Value'].values[0]
    value2 = x_points_dataframe.loc[x_points_dataframe['Y'] == closest_y_values.iloc[1], 'Value'].values[0]
    y1 = closest_y_values.iloc[0]
    y2 = closest_y_values.iloc[1]

    # Calculate the proportion of input_y_mv between the two closest Y values
    proportion = (input_y_mv - y1) / (y2 - y1)

    # Interpolate the value based on the proportion
    estimated_value = value1 + proportion * (value2 - value1)

    return estimated_value

def estimate_date(input_x_date, x_dates_dataframe):
    # Find the two closest X values in the DataFrame
    closest_x_values = x_dates_dataframe['X'].nsmallest(2)
    
    # Extract the corresponding dates and X coordinates
    date1 = pd.to_datetime(x_dates_dataframe.loc[x_dates_dataframe['X'] == closest_x_values.iloc[0], 'Date'].values[0]).date()
    date2 = pd.to_datetime(x_dates_dataframe.loc[x_dates_dataframe['X'] == closest_x_values.iloc[1], 'Date'].values[0]).date()
    x1 = closest_x_values.iloc[0]
    x2 = closest_x_values.iloc[1]

    # Calculate the proportion of input_x_date between the two closest X values
    proportion = (input_x_date - x1) / (x2 - x1)

    # Interpolate the date based on the proportion
    estimated_date = date1 + pd.to_timedelta(proportion * (date2 - date1))

    return estimated_date

def add_date_difference(input_data_points_table, input_x_points_dataframe, input_y_points_dataframe):
    x_points_dataframe = input_x_points_dataframe
    y_points_dataframe = input_y_points_dataframe
    data_points_table = input_data_points_table
    for i in range(0, len(data_points_table)):
        # Handling MV
        this_row_mv_coordinate = data_points_table.at[i, 'Y']
        this_row_mv = estimate_value(this_row_mv_coordinate, x_points_dataframe)
        data_points_table.at[i, 'Market Value'] = this_row_mv

        # Handling Date
        this_row_date_coordinate = data_points_table.at[i, 'X']
        this_row_date = estimate_date(this_row_date_coordinate, y_points_dataframe)
        data_points_table.at[i, 'Date'] = pd.Timestamp(this_row_date)

        # Set appropriate data types
        data_points_table['Market Value'] = data_points_table['Market Value'].astype(float)
        data_points_table['Date'] = pd.to_datetime(data_points_table['Date'], errors='coerce')

    return data_points_table

def findMarketValueFromTable(df, input_date_str):
    # Convert input_date_str to datetime object
    #input_date = datetime.strptime(input_date_str, '%d.%m.%y')
    input_date = process_date_format_for_market_value_table_lookup(input_date_str)

    # Convert the 'Date' column in the DataFrame to datetime objects
    df['Date'] = pd.to_datetime(df['Date'])

    # Calculate the absolute difference between each date and the input date
    #print('input date is: ', input_date, 'first date in table is: ', df.at[0, 'Date'])

    input_date = pd.to_datetime(input_date)


    df['DateDifference'] = abs(df['Date'] - input_date)

    # Find the row with the minimum date difference
    closest_row = df.loc[df['DateDifference'].idxmin()]

    # Get the market value from the closest row
    market_value = closest_row['Market Value']

    # Get the number of days from the game 
    days_from_match = closest_row['DateDifference']

    if(days_from_match.days >= 375):
        print(days_from_match)
        
        return 0#, days_from_match
    else:
        return market_value#, days_from_match
#the return statement from this last function is the market value at that time


# %% [markdown]
# #### Wrapper function

# %%
def seleniumLookUpValueWrapperFunction (input_name_player, input_nationality_player, input_match_date_player):

    selenium_URL, transfermarkt_boolean = getSeleniumURL(input_name_player, input_nationality_player, input_match_date_player) ####add input_date_match

    if(transfermarkt_boolean == True):
        print('transfefrmarkt link boolean true hi')
        #go through with it

        market_value_graph_html = new_seleniumFindMarketValueGraph(selenium_URL) #was seleniumFindMarketValueGraph(selenium_URL)

        if(market_value_graph_html == ""):
            #then it didn't work
            print('wrapper function nayem case working')
            return 0

        else:
            print(selenium_URL)
            axis_points_x, axis_points_y = extract_axis_points(market_value_graph_html)
            print('passed 1')
            data_points_graph = extract_data_points(market_value_graph_html)
            print('passed 2')
            #print(axis_points_x)

            x_points_df = create_x_points_dataframe(axis_points_x)
            print('passed 3')
            #print(axis_points_y)

            y_points_df = create_y_points_dataframe(axis_points_y)
            print('passed 4')
            data_points_table_df = create_data_points_table(data_points_graph)
            print('passed 5')
            data_points_table_df_updated = add_date_difference(data_points_table_df, x_points_df, y_points_df)
            print('passed 6')
            #input_match_date_player

            #findMarketValueFromTable

            result_value_time_of_match = findMarketValueFromTable(data_points_table_df_updated, input_match_date_player)
            print(result_value_time_of_match, '12345')
            return result_value_time_of_match
    else:
        0==0
        #print('Link wasnt transfermarkt, and Searching for links did not yield any results.')
        print('husain ali pele case working')
        return 0 
        ###IMPUTE CASE 5### specific to values 
        


        

# %% [markdown]
# ### SELENIUM Case - SALARIES VERSION

# %% [markdown]
# #### Helper functions

# %%
def find_earnings_history_sections(html_content):
    # Parse the HTML content

    # Find all <div> elements with class="col s12"
    col_s12_elements = html_content.find_all("div", {"class": "content-block"})[0].find_all('div', class_='col s12')

    # List to store the index of correct sections
    correct_section_indices = []

    # Iterate through each col s12 element
    for index, col_s12 in enumerate(col_s12_elements):
        # Check if it contains the expected structure for earnings history
        if col_s12.find('h4', class_='section-title') and col_s12.find('table', class_='table-bordered'):
            correct_section_indices.append(index)

    return correct_section_indices

def process_string_currency(input_value_string):
    if(input_value_string.startswith('$')):
        number_part = int(input_value_string.split('$')[1].replace(',', ''))
        number_part_usd = number_part * 0.91
        return number_part_usd
    
    elif(input_value_string.startswith('€')):
        number_part_eur = int(input_value_string.split('€')[1].replace(',', ''))
        return number_part_eur
    
    elif(input_value_string.startswith('£')):
        number_part = int(input_value_string.split('£')[1].replace(',', ''))
        number_part_gbp = number_part * 1.16
        return number_part_gbp
    
    else:
        print(input_value_string)

def convert_year_to_date(year):
    year = year.split('-')[0]
    # Assuming July 1 for each year
    return datetime(int(year), 7, 1)

def multiply_by_factor(row, input_char_currency):
    if input_char_currency == '$':
        return row * 0.91
    elif input_char_currency == '£':
        return row * 1.16
    else:
        return row
    
def find_closest_date(df, input_date):
    df['Year'] = pd.to_datetime(df['Year'], format='%Y-%m-%d')  # Convert 'Year' column to datetime format
    input_date = pd.to_datetime(input_date, format='%d.%m.%y')  # Convert input_date to datetime format

    closest_date_row = df.iloc[(df['Year'] - input_date).abs().argsort()[0]]
    closest_date_yearly_salary = closest_date_row['Yearly Salary']
    return closest_date_yearly_salary
    

# %%
def compareNames(nameROW, nameURL):
    if(remove_apostrophes_backticks_single_string(nameROW) == createNameFromUrl(nameURL)):
        return True
    if(remove_apostrophes_backticks_single_string(nameROW) in createNameFromUrl(nameURL)):
        return True
    if(createNameFromUrl(nameURL) in remove_apostrophes_backticks_single_string(nameROW)):
        return True
    return False

def createNameFromUrl(input_url_name):
    # Extract name from the URL
    match = re.search(r'/player/([\w-]+)/', input_url_name)
    
    if match:
        raw_name = match.group(1)
        # Remove numbers from the name
        raw_name = re.sub(r'\d', '', raw_name)
        # Split the name into words
        words = re.findall(r'\b\w+\b', raw_name)
        
        # Capitalize words that are two characters or longer
        capitalized_words = []
        for i, word in enumerate(words):
            if len(word) == 1:
                # Handle single characters only if they're the last word in the phrase
                if i == len(words) - 1:
                    if i > 0:
                        capitalized_words[-1] += word
                else:
                    words[i + 1] = word + words[i + 1]
            else:
                capitalized_words.append(word.capitalize())
        
        # Join the words to form the final name
        this_name = ' '.join(capitalized_words)
        
        return this_name


# %% [markdown]
# #### Wrapper Function

# %%
def capology_selenium_lookup(input_name_to_check, input_nationality, input_match_date):
    input_year_test = input_match_date
    natl_test = input_nationality

    if '.' in input_year_test:
        yearstr = input_year_test.split(".")[2]
        full_num = int('20' + yearstr)
    elif '-' in input_year_test:
        if len(input_year_test.split("-")[2]) == 4:
            yearstr = input_year_test.split("-")[2] #this is a 4 digit number
            full_num = int(yearstr)
        elif len(input_year_test.split("-")[2]) == 2:
            if len(input_year_test.split("-")[0]) == 4:
                yearstr = input_year_test.split("-")[0]
                full_num = int(yearstr)
            else:
                yearstr = input_year_test.split("-")[2] #this is a 2 digit number
                full_num = int('20' + yearstr)
        else:
            print('broke on year parsing', input_year_test.split("-"))
        
    full_num = int(full_num)
    #for Ndiaye case use transfermarkt_filtered_result_AAA
    #search = f"{transfermarkt_filtered_result_AAA} {natl_test} capology {full_num}"

    #Zelarayan case
    #search = f"{name_match[2]} {natl_test} capology {full_num}"
    nameforsearch = input_name_to_check
    search = f"{nameforsearch} {natl_test} capology {full_num}"

    url = 'https://www.google.com/search'

    headers = {'Accept' : '*/*', 'Accept-Language': 'en-US,en;q=0.5','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers = headers, params = parameters).text
    soup = BeautifulSoup(content, 'html.parser')

    search = soup.find(id = 'search')
    first_link = search.find('a')

    url_tosplit = (first_link['href'])

    if(compareNames(nameforsearch, url_tosplit)): #name_match[2] #transfermarkt_filtered_result_AAA
        correct_URL_Found = True
        driver = webdriver.Chrome()
        driver.get(url_tosplit)

        # Wait for elements to be present (adjust timeout as needed)
        wait = WebDriverWait(driver, 10)
        
        # Add a retry loop to handle the case where element_text_string is empty
        max_retries = 3
        current_retry = 0
        while current_retry < max_retries:
            elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*")))
            
            element_num = 0
            element_text_string = []
            for element in elements:
                
                if element_num == 0:
                    try:
                        text = element.text

                        # Check if the element contains both "$" signs and "-" characters
                        if "$" in text and "-" in text:
                            element_num += 1
                            element_text_string.append(text)

                    except Exception as e:
                        print(f"Error retrieving text: {e}")

            driver.quit()

            # Check if element_text_string is not empty after retry
            if element_text_string:
                break
            else:
                current_retry += 1
                print(f"Retrying to retrieve text. Retry {current_retry}/{max_retries}")

    else:
        #print('first URL not right')
        # Extract and print text of all links on the first page of Google
        # Extract and print text of all links on the first page of Google
        # Extract and print text of all links on the first page of Google
        all_links = search.find_all('a')
        
        # Counter to keep track of matches found
        match_counter = 0
        name_to_find = remove_apostrophes_backticks_single_string(nameforsearch) #transfermarkt_filtered_result_AAA
        
        for link in all_links:
            try:
                text = link.find('h3').text  # Assuming the result title is wrapped in an 'h3' tag
                url = link.get('href')
                #print(f"Result: {text}\nURL: {url}\n")

                # Check if name_to_find or transfermarkt_filtered_result_AAA is present in the link
                if name_to_find.lower() in url.lower() or "transfermarkt_filtered_result_AAA" in url:
                    print("Match found!", name_to_find, url)
                    match_counter += 1

            except AttributeError:
                pass  # Handle cases where 'h3' tag is not found or has no text

        # Check if no matches were found
        if match_counter == 0:
            #print("No matches found online.")
            correct_URL_Found = False
            #return 0

    if(correct_URL_Found == True):

        if element_text_string:

            split_by_line_elements = element_text_string[0].split('\n')

            correct_elements_indexes_array = []

            for i in range(0, len(split_by_line_elements)):
                if split_by_line_elements[i].startswith('20') and "$" in split_by_line_elements[i]:

                    character_to_split_on = '$'

                    correct_element = split_by_line_elements[i]
                    correct_elements_indexes_array.append(i)

                    #print(i, correct_element)
                elif split_by_line_elements[i].startswith('20') and "€" in split_by_line_elements[i]:

                    character_to_split_on = '€'

                    correct_element = split_by_line_elements[i]
                    correct_elements_indexes_array.append(i)
                    
                elif split_by_line_elements[i].startswith('20') and "£" in split_by_line_elements[i]:

                    character_to_split_on = '£'

                    correct_element = split_by_line_elements[i]
                    correct_elements_indexes_array.append(i)

            rows_list = []

            for j in range(0, len(correct_elements_indexes_array)):
                this_index = correct_elements_indexes_array[j]
                correct_element = split_by_line_elements[this_index]

                this_row_year = correct_element.split(' ')[0]

                correctelement_without_year = correct_element.split(this_row_year)[1][1:]
                split_string = correctelement_without_year.split(character_to_split_on) #'$'

                try:
                    # Extract the numerical values and remove commas
                    number_1 = split_string[1].replace(',', '').strip()
                    number_2 = split_string[2].replace(',', '').strip()
                    number_3 = split_string[3].split('-')[0].replace(',', '').strip()

                    # Extract the team
                    team = split_string[3].split('-')[1].strip()

                    # Append row to the list
                    rows_list.append([number_1, number_2, number_3, team, this_row_year])

                except IndexError:
                    print(j, "Skipping row due to IndexError.")

            # Create a DataFrame
            columns = ["Weekly Salary", "Yearly Salary", "Inflation-Adjusted Yearly Salary", "Team", "Year"]
            df = pd.DataFrame(rows_list, columns=columns)

            df['Year'] = df['Year'].apply(convert_year_to_date)
            columns_to_convert = ['Weekly Salary', 'Yearly Salary', 'Inflation-Adjusted Yearly Salary']

            df[columns_to_convert] = df[columns_to_convert].astype(int)

            # Apply the multiplication based on the character_to_split_on
            df[columns_to_convert] = df[columns_to_convert].apply(lambda x: multiply_by_factor(x, character_to_split_on))

            if(df['Weekly Salary'].sum() == 0):
                ###IMPUTE CASE 6### SPECIFIC TO SALARIES
                0==0
                print('available Capology data shows 0 earnings.')
                return 0

            else:
                #impute_required_salary = False
                closest_date_row = find_closest_date(df, input_year_test)

            return closest_date_row
        
        else:
            print('Unable to retrieve text after multiple attempts.')
            
    else: #didn't find correct URL 
        ###IMPUTE CASE 7### SPECIFIC TO SALARIES
        0==0
        print('no available Capology data or URL page')
        return 0





