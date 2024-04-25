# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import csv


# %%
def grab_transfer_pagesoup(input_url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
    pageTree = requests.get (input_url, headers = headers)
    pageSoup_club = BeautifulSoup (pageTree.content, 'html.parser')
    
    return pageSoup_club

def string_to_datetime(date_string):
    # Define the format of the input date string
    date_format = "%b %d, %Y"  # Example: 'Apr 28, 1987'

    # Convert the string to a datetime object
    datetime_obj = datetime.strptime(date_string, date_format)
    return datetime_obj

def convert_date_format(input_date):
    # Convert the input date string to a datetime object
    date_object = datetime.strptime(input_date, "%b %d, %Y")

    # Convert the datetime object to the desired format "%Y-%m-%d"
    formatted_date = date_object.strftime("%Y-%m-%d")

    return formatted_date

def calculate_age_in_year(birthdate, target_year):
    birthdate = datetime.strptime(birthdate, "%Y-%m-%d")  # Parse the birthdate string
    birth_year = birthdate.year

    if target_year < birth_year:
        return "Invalid input: Target year is before the birth year."

    age_in_year = target_year - birth_year

    # Check if the birthday for the target year has already occurred
    if (birthdate.month, birthdate.day) > (datetime(target_year, datetime.now().month, datetime.now().day).month, datetime.now().day):
        age_in_year -= 1

    return age_in_year

def is_before_july_2005(input_date):
    target_date = datetime(2005, 7, 1)
    return input_date < target_date

def find_age_at_the_time(input_bd, input_szn):
    input_bd = convert_date_format(input_bd)
    return calculate_age_in_year(input_bd, input_szn)

def check_against_stop_date(input_date):
    input_date = string_to_datetime(input_date)
    return is_before_july_2005(input_date)




# %%
def find_alumni_list_2(input_club_name_):


    url_components = find_url_and_code_academy(f"{input_club_name_}")

    previous_page_last_date = ''
    players_names_array = []
    birth_date_array = []
    ages_array = []
    positions_array = []
    nationality_array = []
    teams_played_for_array = [] 
    alive_dead_array = []
    highest_level_played_for_array = []
    at_club_until_array = []
    still_there_array = []

    i = 1

    last_date_before_05 = False
    while (last_date_before_05 == False):
        url_page = f"https://www.transfermarkt.us/{url_components[0]}/alumni/verein/{url_components[1]}/ajax/yw1/buchstabe//land_id/0/position/alle/detailposition/alle/plus/1/sort/im_verein_bis.desc/page/{i}"

        this_page_soup = grab_transfer_pagesoup(url_page)
        #NAMES 
        Players_set = this_page_soup.find_all("td", {"class": "hauptlink"})
        #AGE NATIONALITY CURRENT CLUB 
        zentriert_set = this_page_soup.find_all("td", {"class": "zentriert"})
        #POSITION / TEAMS PLAYED FOR 
        table_set = this_page_soup.find_all("table", {"class": "inline-table"})

        player_index = 0
        zentriert_Index = 0
        table_index = 0

        for j in range(0, int(len(Players_set) / 2)):
        #for j in range(0, 2):
            player_index = (j * 2)
            zentriert_Index = (j * 4)
            table_index = (j * 4)
        #name
            players_names_array.append(Players_set[player_index].text.strip().encode().decode("utf-8"))
        #DOB
            birth_date_array.append(zentriert_set[zentriert_Index].text.strip().encode().decode("utf-8"))
        #pos
            positions_array.append(table_set[table_index].find_all("td")[2].text.strip().encode().decode("utf-8"))
        #natl
            nationality = str(zentriert_set[(zentriert_Index + 2)].find_all("img", {"class": "flaggenrahmen"})).split(' ')
            if (len(nationality) == 5):
                nationality_array.append(nationality[4][7:-4])
            else:
                issit = False
                words_array = []
                words_array.append(nationality[1].split('alt="')[1])
                e = 2
                while(issit == False):
                    #check if it starts with class
                    if(nationality[e].startswith('class')):
                        #end it 
                        issit = True
                        print(nationality[e] + 'false')

                    else:
                        #add it 
                        words_array.append(nationality[e].split('"')[0]) #was "/>]"
                        print(nationality[e])
                        e += 1
                        
                final_name = ' '.join(words_array)
                nationality_array.append(final_name)
        #age
            age = zentriert_set[zentriert_Index + 1].text.strip().encode().decode("utf-8")
            if (age[:1] == '†'):
                alive_dead_array.append('Dead')
                age = int(age[1:])
                ages_array.append(age)
            else:
                alive_dead_array.append('Alive')
                ages_array.append(int(age))
        #teams played for 
            list_of_teams_played_for = table_set[(table_index+2)].find_all("a")
            teams_list_array = []
            for k in range(0, len(list_of_teams_played_for)):
                teams_list_array.append(list_of_teams_played_for[k].text.strip().encode().decode("utf-8"))
            teams_played_for_array.append(teams_list_array)
        #at club until and still there
            if(zentriert_set[zentriert_Index+3].text.strip().encode().decode("utf-8") == "exp. until -"):
                still_there_array.append(True)
                at_club_until_array.append('Still at club')
            else:
                still_there_array.append(False)
                at_club_until_array.append(zentriert_set[zentriert_Index+3].text.strip().encode().decode("utf-8"))
        #highest level played at 
            if(table_set[table_index+3].find("a") is None):
                highest_level_played_for_array.append('No Level')
                #make up a string
            else:
                highest_level_played_for_array.append(table_set[table_index+3].find("a").text.strip().encode().decode("utf-8"))
        #FOR LOOP ENDS
        if (still_there_array[len(still_there_array) - 1] == False):
            previous_page_last_date = zentriert_set[zentriert_Index+3].text.strip().encode().decode("utf-8")

            #do the date logic here
            if (check_against_stop_date(zentriert_set[zentriert_Index+3].text.strip().encode().decode("utf-8"))):
                last_date_before_05 = True
            else:
                last_date_before_05 = False
        
        i += 1

        
        
        #WHEN THE J FOR LOOP ENDS
        #NOTE THE LAST DATE

        #before the while loop begins again, last line i+=1 

    alumni_df_to_return = pd.DataFrame(
    {"Name": players_names_array,
    "Age (2023)": ages_array,
    "Birth Date": birth_date_array,
    "Alive?": alive_dead_array,
    "Nationality": nationality_array,
    "Position": positions_array,
    "Teams Played For": teams_played_for_array,
    "Highest Level Played for": highest_level_played_for_array,
    "Still at club?": still_there_array,
    "At Club Until": at_club_until_array})
    return alumni_df_to_return



