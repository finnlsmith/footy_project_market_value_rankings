#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 19:39:45 2024

@author: tedwards
"""

import pandas as pd
import re
from datetime import datetime, timedelta

def is_within_three_years(date1, date2):
    three_years = timedelta(days=365.25*3)
    print(date1)
    print(date2)
    date1 = datetime(date1)
    date2 = datetime(date2)
    difference = abs(date1-date2)
    if difference <= three_years:
        return True
    else:
        return False
    
def convert_date(input_date):
    formats = ["%d.%m.%y", "%d-%m-%Y", "%d-%b-%y", "%Y-%m-%d"]
    target_format = "%Y-%m-%d"
    
    for date_format in formats:
        try:
            # Try parsing the input date using the current format
            parsed_date = datetime.strptime(input_date, date_format)
            # If successful, convert it to the target format
            result_date = parsed_date.strftime(target_format)
            return result_date
        except ValueError:
            #print(input_date)
            pass
    
    # If none of the formats match, return an error message or handle as needed
    return "Invalid date format"

def extract_name(line):
    cleaned_text = re.sub(r'^\d+\s*', '', line)
    return cleaned_text

def find_single_apps(lookup_df):
    filtered_df = lookup_df.groupby('ORIGINAL.JERSEY').filter(lambda x: len(x) == 1)
    return filtered_df

def get_matching_indicies(lookup_df, lineups_df, lineup_columns):
    matched_details = []
    wrong_lineup = []
    not_matched = []
    count = 0
    for index, row in lookup_df.iterrows():
        name = row['ORIGINAL JERSEY']
        date = row['Date']
        filtered_lookup_date = convert_date(date)
        match_id = row['Match ID']
        competition = row['Competition']
        nationality_code = row['Team Country Code']
        print(name)
        print(nationality_code)
        
        game_lineups = lineups_df[(lineups_df['Match ID'] == match_id)]
        exact_row = game_lineups[(game_lineups[' Code'] == nationality_code)]
        other_row = game_lineups[(game_lineups[' Code'] != nationality_code)]
        print(exact_row[' Code'])
        other_nationality_code = other_row.iloc[0,36]
        in_lineup, in_other_lineup = False, False
        #print(game_lineups)
        if not exact_row.empty:
            for col in lineup_columns:
                lineup_name = extract_name(exact_row.iloc[0][exact_row.columns.get_loc(col)])
                print(lineup_name)
                if name in lineup_name:
                    in_lineup = True
                    matched_details.append({'name': name, 'lineup_name':lineup_name, 'row_index': exact_row.index[0], 'column': col, 'Correct Team': True})
                    break
        """
        #There really ought to be nobody picked up by this besides lineups where dudes have the same last name on opposite teams.
        if not other_row.empty and not in_lineup:
            for col in lineup_columns:
                lineup_name = extract_name(other_row.iloc[0][other_row.columns.get_loc(col)])
                print(lineup_name)
                if name in lineup_name:
                    in_other_lineup = True
                    wrong_lineup.append({'name': name, 'lineup_name':lineup_name, 'row_index': other_row.index[0], 'column': col, 'Correct Team': True})
                    break
        """
        if not in_lineup and not in_other_lineup:
            not_matched.append({'name': name, 'match_id': match_id, 'nationality_code': nationality_code, 'other_nationality_code': other_nationality_code})
        """
        if not exact_row.empty:
            for col in exact_row.iloc[:, 1:32].columns:
                lineup_name = extract_name(exact_row.iloc[0][exact_row.columns.get_loc(col)])
                print(lineup_name)
                #if exact_row.iloc[0][col] == name:
                if name in lineup_name:
                    matched_details.append({'name': name, 'lineup_name':lineup_name, 'row_index': exact_row.index[0], 'column': col, 'Correct Team': True})
                    break
        if not other_row.empty:
            for col in other_row.iloc[:, 1:32].columns:
                lineup_name = extract_name(other_row.iloc[0][other_row.columns.get_loc(col)])
                print(lineup_name)
                if name in lineup_name:
                    matched_details.append({'name': name, 'lineup_name':lineup_name, 'row_index': other_row.index[0], 'column': col, 'Correct Team': False})
                    break
        """
        count +=1
        #if count == 5: break
        found_in_original_lineup = False
        found_in_other_lineup = False
        original_team_games = lineups_df[(lineups_df[' Code'] == nationality_code)]
        other_team_games = lineups_df[(lineups_df[' Code'] == other_nationality_code)]
        
        found_name_original_team = False
        found_name_other_team = False
        
        """
        Here attempting to find if a guy appears in the original listed teams lineup within the past three years. This could have overlap with another person with the same last name. 
        Intended to follow this with checking if he appeared in the other teams lineup in the past three years. 
        If yes, in the original teams lineup with an exact match, some shit is definitely off because how are they in this single appearance filter. 
            If yes, with a partial match, then they should be looked up with partial match name and see if that finds anything in transfermarkt data.
        If yes, in the other teams lineup with an exact match, they could be the that person. Need a jersey check. 
            If yes, with a partial match, then the jersey must be checked. If yes, then they should go in the same bucket as the guys above. If not, their own bucket. 
        If no, in the original team lineup, probably not on the team / can be thrown away. 
        If no, in the other teams lineup, well he didnt play for the other team. 
        """
        for index, row in original_team_games.iterrows():
            game_date = convert_date(row[34])
            print(row)
            print(game_date)
            print("GAME DATE")
            if is_within_three_years(filtered_lookup_date, game_date):
                #Now we look the name up in the columns
                for col in row[1:32].columns:
                    lineup_name = extract_name(row[col])
            
        
    matched_df = pd.DataFrame(matched_details)
    wrong_lineup_df = pd.DataFrame(wrong_lineup)
    not_matched_df = pd.DataFrame(not_matched)
    return matched_df, wrong_lineup_df, not_matched_df
lineup_columns = ['Starter_1','Starter_2','Starter_3','Starter_4','Starter_5','Starter_6','Starter_7','Starter_8',
                  'Starter_9', 'Starter_10', 'Starter_11', 'Sub_1', 'Sub_2', 'Sub_3', 'Sub_4', 'Sub_5', 'Unused_1',
                  'Unused_2','Unused_3','Unused_4','Unused_5','Unused_6','Unused_7','Unused_8','Unused_9','Unused_10',
                  'Unused_11','Unused_12','Unused_13','Unused_14','Unused_15']
lookup_df = pd.read_csv('/Users/tedwards/Downloads/lookup_required_dudes.csv')
filtered_df = lookup_df.groupby('ORIGINAL JERSEY').filter(lambda x: len(x) == 1)
filtered_fiveplusapp_df = lookup_df.groupby('ORIGINAL JERSEY').filter(lambda x: len(x) >= 5)
lineups_df = pd.read_csv('/Users/tedwards/Downloads/newest_lineups_data_march_24.csv')
matched_df, wrong_df, unmatched_df = get_matching_indicies(filtered_df, lineups_df, lineup_columns)