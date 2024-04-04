from fuzzywuzzy import process

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



    #if a row of your DF is "row"
        #this_country_code = row['Team Country Code']

    #leagues value being your big transfermarkt dataset
        #dataset_nationality = leagues_value[leagues_value['Team 1 Code'] == this_country_code]['Name'].unique()
        #dataset_nationality_unidecoded = {unidecode(name) for name in dataset_nationality}
                    




#Pseudo Code
                    
    #first do the threshold match 	
        #if it is someone other than who you have in the row, use them instead 
                    
        #if they are the same person proceed  (try a unidecode equality maybe)
                    

    #do the token matching just in case 
        #this way if the names are not all starting w the same letters we can add them to a list to look up later 

        

