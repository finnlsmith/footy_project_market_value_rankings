#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 14:37:38 2024

@author: tedwards
"""

import pandas as pd

from fuzzywuzzy import process
from Levenshtein import distance
import re
import unidecode

def find_close_matches_variable(this_jersey, dataset_nationality, threshold):
    """
    Find close matches of `this_jersey` in `dataset_nationality` using Levenshtein distance.

    Args:
    - this_jersey (str): The string to find close matches for.
    - dataset_nationality (list): List of strings to search for close matches in.
    - threshold (int): Minimum similarity score required for a match (default is 90).

    Returns:
    - List of strings from `dataset_nationality` that are close matches to `this_jersey`.
    """
    close_matches = process.extract(this_jersey, dataset_nationality, limit=None)
    return [match[0] for match in close_matches if match[1] >= threshold]



#the best function I've got for finding plahyers in the dataset

def threshold_player_match(this_jersey, dataset_nationality):
    THRESHOLD_NUM = 89
    #stops when it returns a name.
    #if it doesnt find a match keep lowering the threshold until you find a match
    #but if you get to threshold of like 50 first you stop and just abandon ship    

    # Loop until someone is found or threshold goes below 50
    while THRESHOLD_NUM >= 50:
        matches = find_close_matches_variable(this_jersey, dataset_nationality, THRESHOLD_NUM)
        if matches:
            #print(f"Player is {this_jersey}. Found matches: {matches}. threshold is {THRESHOLD_NUM}")
            return matches, THRESHOLD_NUM
            #break
        else:
            THRESHOLD_NUM -= 1

    # If threshold reaches below 50 without finding any matches
    if THRESHOLD_NUM < 50:
        return [f"No matches found even with the lowest threshold."], this_jersey #jersey was {this_jersey}
    



#Make sure that the name you have really is the guy that the jersey is of.

#we make sure that for each token in the JERSEY, there's one token that has the same starting letter in the match.  
def vet_tokens_names(name, player):
    player_original = player.copy()
    original_name_tokens = name.split(' ')
    print(original_name_tokens)
    for player_individual in player:
        #print(player)
        this_player_tokens = player_individual.split(' ')
        
        for token in original_name_tokens:
            if token == '':
                0==0
            else:
                first_letter = token[0]
                #print(initial_token)
                token_found = False
                for token_player in this_player_tokens:
                    if token_player.startswith(first_letter):
                        
                        if levenshtein_distance(token_player, token) >= len(token_player):
                            #print(f'did not match {token_player} with {token}')
                            0==0
                        else:
                            #print(f'matched {token_player} with {token}')
                            #print(token_player)
                            token_found = True
                            break
                if not token_found:
                    #print(player)
                    if player_individual in player:
                        player.remove(player_individual)
    #print('banana', player)
    if player  == []:
        player = player_original
        #print('razz', player)
        for player_individual in player:
            this_player_tokens = re.split(r'\s+|-|–', player_individual)
            #print('apple', this_player_tokens)
            for token in original_name_tokens:
                if token == '':
                    0==0
                else:
                    first_letter = token[0]
                    token_found = False
                    for token_player in this_player_tokens:
                        if token_player.startswith(first_letter):
                            #print('pine', token_player)
                            if levenshtein_distance(token_player, token) >= len(token_player):
                                #print(f'did not match {token_player} with {token}')
                                0==0
                            else:
                                #print(f'matched {token_player} with {token}')
                                #print(token_player)
                                token_found = True
                                break
                if not token_found:
                    player.remove(player_individual)
                    break

def find_in_transfermarkt(player_name, season, country_code, transfermarkt_data):
    row = transfermarkt_data[(transfermarkt_data['Name'] == player_name) & (transfermarkt_data['Season'] == season) & (transfermarkt_data['Team 1 Code'] == country_code)]
    if not row.empty:
        #mv = row.iloc[0]['Market Value']
        player_id = row.iloc[0]['PlayerID']
        #team = row.iloc[0]['Team']
        age = row.iloc[0]['Age']
        new_mv, reason = in_season_around(player_id, season, age)
        print(new_mv)
        print(reason)
        if new_mv == -1 or new_mv == 0 or new_mv == "-":
            print("Returning 0 and True")
            return 0, reason
        else:
            print("Returning 0 and False")
            return new_mv, reason
    return 0, "Did Not Find"

def get_club_level(team, season, transfermarkt_data):
    print("h")

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
            if age >= 30:
                return (float(before_season.iloc[0]['Market Value']) * .8), "Only Before"
            else:
                return (float(before_season.iloc[0]['Market Value']) * 1.2), "Only Before"
        else:
            return 0, "Only Before"
    if not after_season.empty and before_season.empty:
        print("Only After Season")
        print(after_season.iloc[0]['Market Value'])
        if after_season.iloc[0]['Market Value'] != "-":
            if age <= 30:
                return (float(after_season.iloc[0]['Market Value']) * .8), "Only After"
            else:
                return (float(after_season.iloc[0]['Market Value']) * 1.2), "Only After"

        else:
            return 0, "Only After"
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
    
        
"""
Here we should create a new df modeled off lookup_df but with two additional columns, 0_Valid and New Value
"""
def go_thru_players(lookup_df, transfermarkt_data, start, stop):
    new_rows = []
    wrong_rows = []
    count = 0
    for index, row in lookup_df.iterrows():
        print(count)
        #print(row)
        if count >= start and count < stop:
            name = row['Name']
            original_jersey = row['ORIGINAL JERSEY']
            season = row['Season']
            country_code = row['Team Country Code']
            print(row['Match ID'])
            #Before calling this function we should call the name checker. 
            dataset_nationality = transfermarkt_data[transfermarkt_data['Team 1 Code'] == country_code]['Name'].unique()
            #dataset_nationality_unidecoded = {unidecode(name) for name in dataset_nationality}
            #transfermarkt_subset = transfermarkt_data[(transfermarkt_data['Team 1 Code'] == country_code) & (transfermarkt_data['Season'] == season)]
            possible_names = threshold_player_match(original_jersey, dataset_nationality)
            #print(name)
            #print(original_jersey)
            #print(possible_names[0][0])
            #print(possible_names)
            found_name = False
            for i in range(len(possible_names[0])):
            #for pot_name in possible_names[0]:
                if possible_names[0][i] == name:
                    new_mv, valid_zero = find_in_transfermarkt(name, season, country_code, transfermarkt_data)
                    new_row = row.to_dict()  # Convert row to dict
                    new_row['Market Value'] = new_mv
                    new_row['Lookup Still Required?'] = "FALSE"
                    new_row['Lookup Return Case'] = valid_zero
                    new_rows.append(new_row)
                    found_name = True
                    break
            if not found_name:
                new_row = row.to_dict()
                new_row['Wrong Name'] = "Yes"
                new_row['Found Name'] = possible_names[0]
                wrong_rows.append(new_row)
        count +=1
    new_df = pd.DataFrame(new_rows)
    wrong_df = pd.DataFrame(wrong_rows)
    return new_df, wrong_df


lookup_df=pd.read_csv('/Users/tedwards/Downloads/large_dataset_had_0.csv')
transfermarkt_data = pd.read_csv('/Users/tedwards/Downloads/Most Updated Edited Transfermarkt Dataset.csv')
new_df, wrong_df = go_thru_players(lookup_df, transfermarkt_data, 0, 6000)
new_df = new_df.drop('Unnamed: 0.1', axis=1)
wrong_df = wrong_df.drop('Unnamed: 0.1', axis=1)



