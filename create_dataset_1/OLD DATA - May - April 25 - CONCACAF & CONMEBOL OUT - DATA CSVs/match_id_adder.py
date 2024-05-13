#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:23:04 2024

@author: tedwards
"""
import pandas as pd
import datetime as datetime

def convert_date(input_date):
    formats = ["%d.%m.%y", "%d-%m-%Y", "%d-%b-%y", "%Y-%m-%d", "%b %d, %Y"]
    target_format = "%Y-%m-%d"
    
    for date_format in formats:
        try:
            # Try parsing the input date using the current format
            parsed_date = datetime.strptime(input_date, date_format)
            # If successful, convert it to the target format
            result_date = parsed_date.strftime(target_format)
            #year = parsed_date.year
            #return year
            return result_date
        except ValueError:
            #print(input_date)
            pass
        
        
old_lineups_data = pd.read_csv('/Users/tedwards/Downloads/newest_lineups_data_march_24.csv')
#old_lineups_data['Formatted Date'] = old_lineups_data['Date'].apply(convert_date)
old_lineups_data['Date'] = pd.to_datetime(old_lineups_data['Date'])
lineups_data = pd.read_csv('/Users/tedwards/Downloads/Match Lineups _ Goals Final Version - v2 World Cup Qualifiers, CONCACAF, Goals.csv')
dates_orig = lineups_data['Date']
lineups_data['Date'] = pd.to_datetime(lineups_data['Date'])

lineups_data['Match ID'] = ""
for index, row in lineups_data.iterrows():
    date = row['Date']
    #date = convert_date(row['Date'])
    date_range = pd.date_range(date - pd.Timedelta(days=1), date + pd.Timedelta(days=1))
    matches = old_lineups_data[(old_lineups_data['Date'].isin(date_range)) & (old_lineups_data[' Code'] == row['Code'])]
    if not matches.empty:
        lineups_data.at[index, 'Match ID'] = matches.iloc[0]['Match ID']
lineups_data['Date'] = dates_orig

