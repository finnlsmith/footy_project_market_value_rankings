#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 10:41:19 2024

@author: tedwards
"""

import pandas as pd
from fuzzywuzzy import process
from Levenshtein import distance
import re
import unidecode

def convert_currency(value):
    # Strip the Euro sign and whitespace
    if value == "-":
        return 0  # Return None or np.nan to represent missing values
    
    value = value.replace('€', '').strip()
    
    # Check the last character to determine the multiplier
    if value[-1].lower() == 'm':
        # Remove the last character and convert to float, then multiply by 1,000,000
        return float(value[:-1]) * 1000000
    elif value[-1].lower() == 'k':
        # Remove the last character and convert to float, then multiply by 1,000
        return float(value[:-1]) * 1000
    else:
        # Just convert to float if there's no 'k' or 'm'
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
    #Returning - means not in either. Otherwise the value will be returned. 0 means the only available row had 0
    if age == "Not Listed": age = 30
    age = int(age)
    year_before = int(curr_season) -1
    year_after = int(curr_season) + 1
    before_season = transfermarkt_data[(transfermarkt_data['PlayerID'] == player_id) & (transfermarkt_data['Season'] == year_before)]
    after_season =  transfermarkt_data[(transfermarkt_data['PlayerID'] == player_id) & (transfermarkt_data['Season'] == year_after)]
    if before_season.empty and after_season.empty:
        print("Both Empty")
        return -1, "Both Empty"
    if not before_season.empty and after_season.empty:
        print("Only Before Season")
        print(before_season.iloc[0]['Market Value'])
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
        print("Only After Season")
        print(after_season.iloc[0]['Market Value'])
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
        print("Need to average")
        #print("Before Season")
        print(before_season.iloc[0]['Market Value'])
        #print("After Season")
        print(after_season.iloc[0]['Market Value'])
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
        #mv = row.iloc[0]['Market Value']
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
            print(new_mv)
            print(reason)
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
    #return 0, "Did Not Find"

def go_thru_players(lookup_df, transfermarkt_data, start, stop):
    new_rows = []
    wrong_rows = []
    count = 0
    for index, row in lookup_df.iterrows():
        #print(count)
        #print(row)
        if count >= start and count < stop:
            name = row['Name']
            original_jersey = row['ORIGINAL JERSEY']
            season = row['Season']
            country_code = row['Team Country Code']
            return_case = row['Lookup Return Case']
            other_name = row['Name(s) Found']
            if return_case == "Did Not Find":
                #print("Case 1")
                #If the name columns are both equal then we actually found the guy 
                if name == other_name:
                    #print("Case 1.1")
                    new_mv, valid_zero = find_in_transfermarkt(name, season, country_code, transfermarkt_data)
                    new_row = row.to_dict()
                    new_row['Market Value'] = new_mv
                    new_row['Lookup Still Required?'] = "FALSE"
                    new_row['Lookup Return Case'] = valid_zero
                    new_row['Status'] = "SUCCESS"
                    new_rows.append(new_row)
                else:
                    #dataset_nationality = transfermarkt_data[transfermarkt_data['Team 1 Code'] == country_code]['Name'].unique()
                    #possible_names = threshold_player_match(original_jersey, dataset_nationality)
                    
                    #Hold off on trying to match these dudes 
                    new_row = row.to_dict()
                    new_row['Lookup Still Required?'] = "TRUE"
                    new_row['Lookup Return Case'] = "Found Different Names"
                    new_row['Status'] = "FAIL"
                    wrong_rows.append(new_row)

            else: 
                new_row = row.to_dict()
                new_rows.append(new_row)
            #print(row['Match ID'])
        count +=1
    new_df = pd.DataFrame(new_rows)
    wrong_df = pd.DataFrame(wrong_rows)
    return new_df, wrong_df

pd.set_option('display.float_format', '{:.2f}'.format)
lookup_df=pd.read_csv('/Users/tedwards/Downloads/updated Terrell new DF.csv')
#lookup_df_wrong = lookup_df[lookup_df['Lookup Return Case'] == "Did Not Find"]
transfermarkt_data = pd.read_csv('/Users/tedwards/Desktop/Files and Images/Python Programs/MarketValues.csv')
transfermarkt_data['Market Value'] = transfermarkt_data['Market Value'].apply(convert_currency)
new_df, wrong_df = go_thru_players(lookup_df, transfermarkt_data, 0, 11000)
new_df = new_df.drop('Unnamed: 0.1.1', axis=1)
new_df = new_df.drop('Unnamed: 0.1', axis = 1)
#wrong_df = wrong_df.drop('Unnamed: 0.1', axis=1)







