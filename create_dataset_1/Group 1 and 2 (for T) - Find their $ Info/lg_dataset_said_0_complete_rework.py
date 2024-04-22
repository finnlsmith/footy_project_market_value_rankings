#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 11:23:44 2024

@author: tedwards
"""

import pandas as pd
from fuzzywuzzy import process
from Levenshtein import distance
import re
import unidecode

    
def process_string(item):
    item = str(item)
    if '[' in item and ']' in item:
        # Extract the substring between the first '[' and the last ']'
        content = item[item.find('[') + 1:item.rfind(']')].strip()
        if ',' in content:
            return "MULTIPLE"
        else:
            # Remove leading and trailing spaces and quotes
            return content.strip("'\" ")
    else:
        return item

def convert_currency(value):
    # Strip the Euro sign and whitespace + convert to float and parse k/m
    if value == "-":
        return 0  
    value = value.replace('€', '').strip()
    if value[-1].lower() == 'm':
        return float(value[:-1]) * 1000000
    elif value[-1].lower() == 'k':
        return float(value[:-1]) * 1000
    else:
        return float(value)
    
def find_close_matches_variable(this_jersey, dataset_nationality, threshold):
    close_matches = process.extract(this_jersey, dataset_nationality, limit=None)
    return [match[0] for match in close_matches if match[1] >= threshold]

def threshold_player_match(this_jersey, dataset_nationality):
    THRESHOLD_NUM = 89
    
    while THRESHOLD_NUM >= 50:
        matches = find_close_matches_variable(this_jersey, dataset_nationality, THRESHOLD_NUM)
        if matches:
            #print(f"Player is {this_jersey}. Found matches: {matches}. threshold is {THRESHOLD_NUM}")
            return matches, THRESHOLD_NUM
        else:
            THRESHOLD_NUM -= 1
    if THRESHOLD_NUM < 50:
        return [f"No matches found even with the lowest threshold."], this_jersey #jersey was {this_jersey}
    
    
def in_season_around(player_id, curr_season, age):
    if age == "Not Listed": age = 30
    age = int(age)
    year_before = int(curr_season) -1
    year_after = int(curr_season) + 1
    before_season = transfermarkt_data[(transfermarkt_data['PlayerID'] == player_id) & (transfermarkt_data['Season'] == year_before)]
    after_season =  transfermarkt_data[(transfermarkt_data['PlayerID'] == player_id) & (transfermarkt_data['Season'] == year_after)]
    if before_season.empty and after_season.empty:
        #print("Both Empty")
        return -1, "Both Empty"
    if not before_season.empty and after_season.empty:
        #print("Only Before Season")
        #print(before_season.iloc[0]['Market Value'])
        if before_season.iloc[0]['Market Value'] != "-":
            if before_season.iloc[0]['Market Value'] == 0:
                return 0, "Only Before + Zero Before"
            else:
                if age >= 30:
                    return (float(before_season.iloc[0]['Market Value']) * .8), "Only Before"
                else:
                    return (float(before_season.iloc[0]['Market Value']) * 1.2), "Only Before"
        else:
            return 0, "Only Before X"
    if not after_season.empty and before_season.empty:
        #print("Only After Season")
        #print(after_season.iloc[0]['Market Value'])
        if after_season.iloc[0]['Market Value'] != "-":
            if after_season.iloc[0]['Market Value'] == 0:
                return 0, "Only After + Zero After"
            else:
                if age <= 30:
                    return (float(after_season.iloc[0]['Market Value']) * .8), "Only After"
                else:
                    return (float(after_season.iloc[0]['Market Value']) * 1.2), "Only After"

        else:
            return 0, "Only After X"
    if not before_season.empty and not after_season.empty:
        #print("Need to average")
        #print("Before Season")
        #print(before_season.iloc[0]['Market Value'])
        #print("After Season")
        #print(after_season.iloc[0]['Market Value'])
        before_season_val = before_season.iloc[0]['Market Value']
        after_season_val = after_season.iloc[0]['Market Value']
        if before_season_val != "-" and after_season_val != "-":
            return ((float(before_season.iloc[0]['Market Value']) + float(after_season.iloc[0]['Market Value'])) / 2), "Used Average of Season Before and After"
        elif before_season_val != "-" and after_season_val == "-":
            if age >= 30:
                return (float(before_season.iloc[0]['Market Value']) * .8), "Used Season Before * .8 But Had Both"
            else:
                return (float(before_season.iloc[0]['Market Value']) * 1.2), "Used Season Before * 1.2 But Had Both"
        elif before_season_val == "-" and after_season_val != "-":
            if age <= 30:
                return (float(after_season.iloc[0]['Market Value']) * .8), "Used Season After * .8 But Had Both"
            else:
                return (float(after_season.iloc[0]['Market Value']) * 1.2), "Used Season After * 1.2 But Had Both"
        else:
            return 0, "Had Both but Both Were Empty"
        
def find_in_transfermarkt(player_name, season, country_code, transfermarkt_data):
    row = transfermarkt_data[(transfermarkt_data['Name'] == player_name) & (transfermarkt_data['Season'] == season) & (transfermarkt_data['Team 1 Code'] == country_code)]
    one_up_row = transfermarkt_data[(transfermarkt_data['Name'] == player_name) & (transfermarkt_data['Season'] == int(season)+1) & (transfermarkt_data['Team 1 Code'] == country_code)]
    one_down_row = transfermarkt_data[(transfermarkt_data['Name'] == player_name) & (transfermarkt_data['Season'] == int(season)-1) & (transfermarkt_data['Team 1 Code'] == country_code)]
    if not row.empty:
        player_id = row.iloc[0]['PlayerID']
        #team = row.iloc[0]['Team']
        age = row.iloc[0]['Age']
        #Here we should be checking if the row 
        marketval = row.iloc[0]['Market Value']
        if marketval != 0:
            print(f"Found in Curr Season: {marketval}")
            return marketval, "Found in Curr Season"
        else:
            new_mv, reason = in_season_around(player_id, season, age)
            print("Not in Curr Season")
            #print(new_mv)
            #print(reason)
            if new_mv == -1 or new_mv == 0 or new_mv == "-":
                print("Returning 0 and True")
                return 0, reason
            else:
                print("Returning 0 and False")
                return new_mv, reason
    elif not one_up_row.empty:
        player_id = one_up_row.iloc[0]['PlayerID']
        age = one_up_row.iloc[0]['Age']
        #marketval = one_up_row.iloc[0]['Market Value']
        new_mv, reason = in_season_around(player_id, season, age)
        if new_mv == -1 or new_mv == 0 or new_mv == "-":
            print("Returning 0 and True")
            return 0, reason
        else:
            print("Returning 0 and False")
            return new_mv, reason
    elif not one_down_row.empty:
        player_id = one_down_row.iloc[0]['PlayerID']
        age = one_down_row.iloc[0]['Age']
        new_mv, reason = in_season_around(player_id, season, age)
        if new_mv == -1 or new_mv == 0 or new_mv == "-":
            print("Returning 0 and True")
            return 0, reason
        else:
            print("Returning 0 and False")
            return new_mv, reason
    else:
        return 0, "Did Not Find in Curr Season, One Up, or One Down"

def go_thru_players(lookup_df, transfermarkt_data, start, stop):
    new_rows = []
    wrong_rows = []
    count = 0
    for index, row in lookup_df.iterrows():
        #print(count)
        #print(row)
        if count >= start and count < stop:
            name = row['Name(s) Found']
            original_jersey = row['ORIGINAL JERSEY']
            season = row['Season']
            country_code = row['Team Country Code']
            #return_case = row['Lookup Return Case']
            #other_name = row['Name(s) Found']
            #third_name = row['New Found Name']
            #Here we cannot use return_case = "Did Not Find"
            
            #if return_case == "Did Not Find":
                #print("Case 1")
                #If the name columns are both equal then we actually found the guy 
            #Unindenting because every row ought to be checked.
            print(name)
            #name_2 = eval(row["Names_Found"])
            print(process_string(name))
            name = process_string(name)
            #print(check_names_type(eval(row["Names_Found"])))
            if process_string(name) != "MULTIPLE":
                print(f"in single name {name}")
                new_mv, valid_zero = find_in_transfermarkt(name, season, country_code, transfermarkt_data)
                if valid_zero != "Did Not Find in Curr Season, One Up, or One Down":
                    new_row = row.to_dict()
                    new_row['Market Value'] = new_mv
                    new_row['Lookup Still Required?'] = "FALSE"
                    new_row['Lookup Return Case'] = valid_zero
                    new_row['Status'] = "SUCCESS"
                    new_rows.append(new_row)
                else:
                    new_row = row.to_dict()
                    new_row['Lookup Still Required?'] = "TRUE"
                    new_row['Lookup Return Case'] = "Failed Using Name Looking at Season and Season +-1"
                    new_row['Status'] = "FAIL"
                    wrong_rows.append(new_row)
                    
                    """
            elif check_names_type(name) == "List One Name":
                name_str = name[0]
                print(f"in list {name_str}")
                new_mv, valid_zero = find_in_transfermarkt(name_str, season, country_code, transfermarkt_data)
                if valid_zero != "Did Not Find in Curr Season, One Up, or One Down":
                    new_row = row.to_dict()
                    new_row['Market Value'] = new_mv
                    new_row['Lookup Still Required?'] = "FALSE"
                    new_row['Lookup Return Case'] = valid_zero
                    new_row['Status'] = "SUCCESS"
                    new_rows.append(new_row)
                else:
                    new_row = row.to_dict()
                    new_row['Lookup Still Required?'] = "TRUE"
                    new_row['Lookup Return Case'] = "Failed Using Name Looking at Season and Season +-1"
                    new_row['Status'] = "FAIL"
                    wrong_rows.append(new_row)
                    """
            else:
                new_row = row.to_dict()
                new_row['Lookup Still Required?'] = "TRUE"
                new_row['Lookup Return Case'] = "Name Confusion"
                new_row['Status'] = "FAIL"
                wrong_rows.append(new_row)
            """
            if name == other_name and name == third_name:
                #print("Case 1.1")
                new_mv, valid_zero = find_in_transfermarkt(name, season, country_code, transfermarkt_data)
                if valid_zero != "Did Not Find":
                    new_row = row.to_dict()
                    new_row['Market Value'] = new_mv
                    new_row['Lookup Still Required?'] = "FALSE"
                    new_row['Lookup Return Case'] = valid_zero
                    new_row['Status'] = "SUCCESS"
                    new_rows.append(new_row)
                else:
                    new_row = row.to_dict()
                    new_row['Lookup Still Required?'] = "TRUE"
                    new_row['Lookup Return Case'] = "Failed Using Name"
                    new_row['Status'] = "FAIL"
                    wrong_rows.append(new_row)
            elif check_names_type(third_name) == "Single Name":
                new_mv, valid_zero = find_in_transfermarkt(third_name, season, country_code, transfermarkt_data)
                if valid_zero != "Did Not Find":
                    new_row = row.to_dict()
                    new_row['Market Value'] = new_mv
                    new_row['Lookup Still Required?'] = "FALSE"
                    new_row['Lookup Return Case'] = valid_zero
                    new_row['Status'] = "SUCCESS"
                    new_rows.append(new_row)
                else:
                    new_row = row.to_dict()
                    new_row['Lookup Still Required?'] = "TRUE"
                    new_row['Lookup Return Case'] = "Failed Using New Found Name"
                    new_row['Status'] = "FAIL"
                    wrong_rows.append(new_row)
            else:
                #dataset_nationality = transfermarkt_data[transfermarkt_data['Team 1 Code'] == country_code]['Name'].unique()
                #possible_names = threshold_player_match(original_jersey, dataset_nationality)
                
                #Hold off on trying to match these dudes 
                new_row = row.to_dict()
                new_row['Lookup Still Required?'] = "TRUE"
                new_row['Lookup Return Case'] = "Name Confusion"
                new_row['Status'] = "FAIL"
                wrong_rows.append(new_row)
            """
            """
            else: 
                new_row = row.to_dict()
                new_rows.append(new_row)
            """
            #print(row['Match ID'])
        count +=1
    new_df = pd.DataFrame(new_rows)
    wrong_df = pd.DataFrame(wrong_rows)
    return new_df, wrong_df

pd.set_option('display.float_format', '{:.2f}'.format)
lookup_df=pd.read_csv('/Users/tedwards/Downloads/lg_dataset_said_0_complete.csv')
#lookup_df_wrong = lookup_df[lookup_df['Lookup Return Case'] == "Did Not Find"]
transfermarkt_data = pd.read_csv('/Users/tedwards/Desktop/Files and Images/Python Programs/MarketValues.csv')
transfermarkt_data['Market Value'] = transfermarkt_data['Market Value'].apply(convert_currency)
new_df, wrong_df = go_thru_players(lookup_df, transfermarkt_data, 0, 11000)
#new_df = new_df.drop('Unnamed: 0.1.1', axis=1)
#new_df = new_df.drop('Unnamed: 0.1', axis = 1)
#wrong_df = wrong_df.drop('Unnamed: 0.1', axis=1)







