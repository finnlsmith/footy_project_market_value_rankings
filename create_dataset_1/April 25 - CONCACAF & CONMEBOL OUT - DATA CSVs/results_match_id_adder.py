#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 22:24:05 2024

@author: tedwards
"""

import pandas as pd
import datetime as datetime
from datetime import timedelta
import json

def convert_date(input_date):
    formats = ["%d.%m.%y", "%d-%m-%Y", "%d-%b-%y", "%Y-%m-%d", "%b %d, %Y"]
    target_format = "%Y-%m-%d"
    
    for date_format in formats:
        try:
            # Try parsing the input date using the current format
            parsed_date = datetime.strptime(input_date, date_format)
            # If successful, convert it to the target format
            result_date = parsed_date.strftime(target_format)
            year = parsed_date.year
            #return year
            return result_date
        except ValueError:
            #print(input_date)
            pass
        
def format_date(date):
    return date.strftime('%d-%b-%y')
    #return datetime.strftime(date, '%d-%b-%y')

def get_value_from_dict(key, dictionary):
    return dictionary.get(key, "Key not found")

def add_codes_to_results(codes_df, new_lineup_df, old_lineup_df):
    new_rows=[]
    for index, row in new_lineup_df.iterrows():
        country_one_name = row[1]
        country_two_name = row[2]
        new_row = row.to_dict()
        date = row[4]
        parsed_date_new = convert_date(date)
        
        country_one_row = codes_df[codes_df['Country'] == country_one_name]
        country_two_row = codes_df[codes_df['Country'] == country_two_name]
        #print(country_one_row)
        if(len(country_one_row) != 1):
            print(country_one_name)
        if(len(country_two_row) != 1):
            print(country_two_name)
        
        if(len(country_one_row)== 1 and len(country_two_row) == 1):
            country_one_code = country_one_row.iloc[0][2]
            country_two_code = country_two_row.iloc[0][2]
            
            new_row['Team 1 Code'] = country_one_code
            new_row['Team 2 Code'] = country_two_code
            new_rows.append(new_row)
        
        
    new_df = pd.DataFrame(new_rows)
    return new_df
        

def add_codes_to_lineups(codes_df, lineup_df):
    new_rows =[]
    for index, row in lineup_df.iterrows():
        country_name = row[1]
        new_row = row.to_dict()
        
        country_row = codes_df[codes_df['Country'] == country_name]
        if(len(country_row) != 1):
            print(country_name)
        else:
            country_code = country_row.iloc[0][2]
            new_row['Code'] = country_code
            new_rows.append(new_row)
    new_df = pd.DataFrame(new_rows)
    return new_df

def create_keys(row):
    base_date = row['Date']
    prev_date = base_date - timedelta(days=1)  # Adjust by subtracting one day
    next_date = base_date + timedelta(days=1)  # Adjust by adding one day
    key1 = f"{row['Match']}:{base_date.strftime('%d-%b-%y')}"
    key2 = f"{row['Match']}:{prev_date.strftime('%d-%b-%y')}"
    key3 = f"{row['Match']}:{next_date.strftime('%d-%b-%y')}"
    return key1, key2, key3

def check_dictionary(keys, results):
    for key in keys:
        if key in results:
            return results[key]
    return "Key not found"

#country_codes = pd.read_csv('/Users/tedwards/Downloads/countries_and_codes (1).csv')
lineups_data = pd.read_csv('/Users/tedwards/Downloads/Match Lineups _ Goals Final Version - v2 World Cup Qualifiers, CONCACAF, Goals.csv')
file_path = '/Users/tedwards/Downloads/matches_IDs_dict.json'

# Open the JSON file and load its contents into a dictionary
with open(file_path, 'r') as file:
    data_dict = json.load(file)

lineups_data['Date'] = pd.to_datetime(lineups_data['Date'])
lineups_data['Possible Keys'] = lineups_data.apply(create_keys, axis=1)

#lineups_data['Key'] = lineups_data['Match'] + ':' + lineups_data['Date'].apply(format_date)
lineups_data['Found?'] = False
lineups_data['Match ID'] = lineups_data['Possible Keys'].apply(lambda x: check_dictionary(x, data_dict))
#lineups_data['Match ID'] = lineups_data['Key'].apply(lambda x: get_value_from_dict(x, data_dict))
#lineups_data_with = lineups_data.drop('Key', axis=1)


#old_lineups_data = pd.read_csv('/Users/tedwards/Downloads/newest_lineups_data_march_24.csv')
#old_lineups_data['Formatted Date'] = old_lineups_data['Date'].apply(convert_date)
#lineups_data_w_code_and_id = add_codes_to_results(country_codes, lineups_data, old_lineups_data)
#lineups_with_code = add_codes_to_lineups(country_codes, lineups_data)




