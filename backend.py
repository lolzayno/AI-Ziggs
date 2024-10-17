import os
import json
import requests
import pytz
import datetime
from sqlalchemy import create_engine, text
from datetime import datetime
import time
import string

#fetches rune mapping
def fetch_rune(patch):

    url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/runesReforged.json"
    

    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to fetch runes data. Status code: {response.status_code}")
        return None
    
    
    rune_data = response.json()
    rune_mappings = {}
    

    for tree in rune_data:
        for slot in tree['slots']:
            for rune in slot['runes']:
                rune_mappings[rune['id']] = rune['name']
    
    return rune_mappings

#fetches item mapping
def fetch_item(patch):
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/item.json"
    response = requests.get(url)
    item_data = response.json()

    # Mapping item_id to a dictionary with 'name', 'status', and 'gold' (total cost)
    item_mapping = {
        int(item_id): {
            'name': item_info['name'],
            'status': 'completed' if 'into' not in item_info else 'component',
            'gold': item_info['gold']['total']  # Get the total gold cost
        } 
        for item_id, item_info in item_data['data'].items()
    }

    # Map 0 to 'None' with a status of 'none' and gold cost of 0
    item_mapping[0] = {'name': 'None', 'status': 'none', 'gold': 0}
    
    return item_mapping

def champ_map(patch):
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json'
    response = requests.get(url)
    
    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()
        
        # Create a translation table for removing punctuation
        translator = str.maketrans('', '', string.punctuation)

        # Function to clean the champion name
        def clean_champion_name(name):
            # Remove apostrophes
            name = name.replace("'", "")
            # Replace spaces with no space and uppercase the next character
            name = ''.join(word.capitalize() for word in name.split())
            return name
        
        # Create a mapping from cleaned champion names to their IDs
        champion_data = {clean_champion_name(champ['name']): champ['key'] for champ in data['data'].values()}
        champion_data['KogMaw'] = champion_data.pop('Kogmaw')
        champion_data['DrMundo'] = champion_data.pop('Dr.Mundo')
        champion_data['FiddleSticks'] = champion_data.pop('Fiddlesticks')
        champion_data['KSante'] = champion_data.pop('Ksante')
        champion_data['Nunu'] = champion_data.pop('Nunu&Willump')
        champion_data['JarvanIV'] = champion_data.pop('JarvanIv')
        champion_data['MonkeyKing'] = champion_data.pop('Wukong')
        champion_data['RekSai'] = champion_data.pop('Reksai')
        champion_data['Renata'] = champion_data.pop('RenataGlasc')
        return champion_data
    else:
        print(f"Error: {response.status_code}")
        return None

#connects to database
def establish_connection():
    engine = create_engine(f'mysql+mysqlconnector://{get_json("user")}:{get_json("host_pw")}@{get_json("host_host")}/{get_json("database")}')
    try:
        with engine.connect() as connection:
            print("Connection to the database was successful!")
    except Exception as e:
        print(f"Error: {e}")

    return engine

#fetches stuff from json file
def get_json(subject):
    script_dir = os.path.dirname(__file__)

    config_path = os.path.join(script_dir,'config.json')

    with open(config_path, 'r') as file:
        config = json.load(file)

    return config.get(subject)

#Fetches challenger players
def fetch_challenger(region, api_key):
    challenger_link = f'https://{region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(challenger_link)
    print("Fetching Challenger Players")
    print(response.status_code)
    time.sleep(1)
    return response.json()

#fetches grandmaster players
def fetch_grandmaster(region, api_key):
    grandmaster_link = f'https://{region}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(grandmaster_link)
    print("Fetching Grandmaster Players")
    print(response.status_code)
    time.sleep(1)
    return response.json()

#fetches master players
def fetch_master(region, api_key):
    master_link = f'https://{region}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(master_link)
    print("Fetching Mater Players")
    print(response.status_code)
    time.sleep(1)
    return response.json()

#fetches matches of user
def fetch_matches(region, fetched_id, api_key, season_start):
    if region in ['BR1', 'LA1', 'LA2', 'NA1', 'OC1']:
        region = 'americas'
    elif region in ['JP1', 'KR']:
        region = 'asia'
    elif region in ['EUW1', 'EUN1', 'RU', 'TR1', 'ME1']:
        region = 'europe'
    else:
        region = 'sea'

    type_match = 'ranked'
    starting_index = 0
    matches_requested = 100
    all_matches = []
    while True:
        matches_api_url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{fetched_id}/ids?startTime={season_start}&type={type_match}&start={starting_index}&count={matches_requested}&api_key={api_key}'
        response = requests.get(matches_api_url)
        print("Fetching Matches")
        print(response.status_code)
        if response.status_code != 200:
            print(f"Error fetching matches: {response.status_code}")
            break
        bundled_matches = response.json()
        if not bundled_matches:
            break
            
        all_matches.extend(bundled_matches)
        

        starting_index += matches_requested

    return all_matches

#fetches puuid of user
def get_puuid(summoner_id, api_key, region):
    get_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}'
    response = requests.get(get_url)
    print("Fetching puuid")
    print(response.status_code)
    return response.json()['puuid']

#get ign and tag
def get_ign(puuid, api_key, region):
    if region in ['BR1', 'LA1', 'LA2', 'NA1', 'OC1']:
        region = 'americas'
    elif region in ['JP1', 'KR', 'PH2', 'SG2', 'TH2', 'TW2', 'VN2']:
        region = 'asia'
    elif region in ['EUW1', 'EUN1', 'RU', 'TR1', 'ME1']:
        region = 'europe'
    get_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}"
    response = requests.get(get_url)
    print("Fetching IGN")
    print(response.status_code)
    data = response.json()
    return data['gameName'], data['tagLine']

def update_players(player_list, engine, region, api_key, rank):
    for player in player_list['entries']:
        time.sleep(1)
        puuid = get_puuid(player['summonerId'], api_key, region)
        ign, tag = get_ign(puuid, api_key, region)
        insert_player(engine, player['summonerId'], puuid, ign, tag, region, rank, player['leaguePoints'], player['wins'], player['losses'], datetime.now())
#Updating and inserting player
def insert_player(engine, summoner_id, puuid, summoner_name, summoner_tag, summoner_region, summoner_rank, summoner_lp, summoner_wins, summoner_losses, last_updated):
    check_sql = """
    SELECT COUNT(*) FROM highelo_player
    WHERE summoner_id = :summoner_id
    """
    update_sql = """
    UPDATE highelo_player
    SET 
        puuid = :puuid,
        summoner_name = :summoner_name,
        summoner_tag = :summoner_tag,
        summoner_region = :summoner_region,
        summoner_rank = :summoner_rank,
        summoner_lp = :summoner_lp,
        summoner_wins = :summoner_wins,
        summoner_losses = :summoner_losses,
        last_updated = :last_updated
    WHERE summoner_id = :summoner_id
    """
    insert_sql = """
    INSERT INTO highelo_player(summoner_id, puuid, summoner_name, summoner_tag, summoner_region, summoner_rank, summoner_lp, summoner_wins, summoner_losses, last_updated) VALUES (:summoner_id, :puuid, :summoner_name, :summoner_tag, :summoner_region, :summoner_rank, :summoner_lp, :summoner_wins, :summoner_losses, :last_updated)
    """
    fetch_sql = """
    SELECT * FROM highelo_player
    WHERE summoner_id = :summoner_id
    """
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            result = connection.execute(text(check_sql), {
                "summoner_id": summoner_id
            })
            count = result.scalar()
            if count > 0:
                connection.execute(text(update_sql), {
                    "summoner_id": summoner_id,
                    "puuid": puuid,
                    "summoner_name": summoner_name, 
                    "summoner_tag": summoner_tag, 
                    "summoner_region": summoner_region, 
                    "summoner_rank": summoner_rank, 
                    "summoner_lp": summoner_lp, 
                    "summoner_wins": summoner_wins,
                    "summoner_losses": summoner_losses, 
                    "last_updated": last_updated
                })
            else:
                time_zone = pytz.timezone('America/Los_Angeles')
                season_start = datetime(2024, 9, 25, 12, 0, 0, tzinfo=time_zone)
                connection.execute(text(insert_sql), {
                    "summoner_id": summoner_id,
                    "puuid": puuid,
                    "summoner_name": summoner_name, 
                    "summoner_tag": summoner_tag, 
                    "summoner_region": summoner_region, 
                    "summoner_rank": summoner_rank, 
                    "summoner_lp": summoner_lp, 
                    "summoner_wins": summoner_wins, 
                    "summoner_losses": summoner_losses, 
                    "last_updated": season_start
                })
            transaction.commit()
            result = connection.execute(text(fetch_sql), {
                "summoner_id": summoner_id
            })
            player = result.fetchone()
            if player:
                return player
            else:
                return None
        except Exception as e:
            transaction.rollback()
            raise e

def get_timeline(region, match_code, api_key, puuid, item_map, item0, item1, item2, item3, item4, item5):
    timeline_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_code}/timeline?api_key={api_key}"
    time.sleep(1)
    response = requests.get(timeline_url)
    print(response.status_code)
    data = response.json()
    item_list = []
    component_list = []
    sup_id = None
    final_items = [item0, item1, item2, item3, item4, item5]
    if 3869 in [item0, item1, item2, item3, item4, item5]:
        sup_id = 3869
    elif 3870 in [item0, item1, item2, item3, item4, item5]:
        sup_id = 3870
    elif 3871 in [item0, item1, item2, item3, item4, item5]:
        sup_id = 3871
    elif 3876 in [item0, item1, item2, item3, item4, item5]:
        sup_id = 3876
    elif 3877 in [item0, item1, item2, item3, item4, item5]:
        sup_id = 3877
    for x, player in enumerate(data['metadata']['participants']):
        if player == puuid:
            participantid = x + 1
            break
    for x in range(len(data['info']['frames'])):
        for item in data['info']['frames'][x]['events']:
            if item['type'] == 'ITEM_PURCHASED':
                if item['participantId'] == participantid:
                    item_id = item['itemId']
                    if item_id in final_items:
                        if item_map[item_id]['status'] == 'completed' and item_map[item_id]['gold'] > 900:
                            item_list.append(item_id)  # Add completed items to item_list
                        else:
                            component_list.append(item_id)  # Add components to component_list
                        final_items = [item for item in final_items if item != item_id]
                    elif item_id == "3865":
                        if sup_id is None:
                            item_list.append(item_id)
                        else:
                            item_list.append(sup_id)
    # component_list = sorted(component_list, key=lambda x: x['gold'], reverse=True)
    # component_list = [item['name'] for item in component_list]
    full_list = item_list + component_list
    final_list = []
    for x in range(6):
        if x < len(full_list):
            final_list.append(full_list[x])
        else:
            final_list.append(0)
    return final_list[0], final_list[1], final_list[2], final_list[3], final_list[4], final_list[5]

#fetches specific match data 
def fetch_match_data(match_id, api_key, region):
    if region in ['BR1', 'LA1', 'LA2', 'NA1', 'OC1']:
        region = 'americas'
    elif region in ['JP1', 'KR']:
        region = 'asia'
    elif region in ['EUW1', 'EUN1', 'RU', 'TR1', 'ME1']:
        region = 'europe'
    else:
        region = 'sea'
    #api url request link to riot
    specific_match_api_url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    #actual request
    response = requests.get(specific_match_api_url)
    print(f"Fetching Match Specific Data: {match_id}")
    print(response.status_code)
    data = response.json()
    timestamp = data['info']['gameEndTimestamp']
    timestamp = timestamp / 1000.0
    timestamp = datetime.fromtimestamp(timestamp)
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    gameduration = data['info']['gameDuration']
    if gameduration <= 300:
        return None
    if data['info']['participants'][0]['win'] == True:
        result = 'Blue'
    else:
        result = 'Red'
    for count, player in enumerate(data['info']['participants']):
        try:
            if player['teamPosition'] == 'TOP' and player['teamId'] == 100:
                bluetop_id = data['info']['participants'][count]['summonerId']
                bluetop_champ = data['info']['participants'][count]['championName']
                bluetop_kills = data['info']['participants'][count]['kills']
                bluetop_deaths = data['info']['participants'][count]['deaths']
                bluetop_assists = data['info']['participants'][count]['assists']
                bluetop_kda = data['info']['participants'][count]['challenges']['kda']
                bluetop_item0 = data['info']['participants'][count]['item0']
                bluetop_item1 = data['info']['participants'][count]['item1']
                bluetop_item2 = data['info']['participants'][count]['item2']
                bluetop_item3 = data['info']['participants'][count]['item3']
                bluetop_item4 = data['info']['participants'][count]['item4']
                bluetop_item5 = data['info']['participants'][count]['item5']
                bluetop_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                bluetop_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                bluetop_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                bluetop_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                bluetop_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                bluetop_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                bluetop_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                bluetop_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                bluetop_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                bluetop_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                bluetop_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                bluetop_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                bluetop_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5 = get_timeline(region, match_id, api_key, puuid, item_map, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5)
            elif player['teamPosition'] == 'TOP' and player['teamId'] == 200:
                redtop_id = data['info']['participants'][count]['summonerId']
                redtop_champ = data['info']['participants'][count]['championName']
                redtop_kills = data['info']['participants'][count]['kills']
                redtop_deaths = data['info']['participants'][count]['deaths']
                redtop_assists = data['info']['participants'][count]['assists']
                redtop_kda = data['info']['participants'][count]['challenges']['kda']
                redtop_item0 = data['info']['participants'][count]['item0']
                redtop_item1 = data['info']['participants'][count]['item1']
                redtop_item2= data['info']['participants'][count]['item2']
                redtop_item3 = data['info']['participants'][count]['item3']
                redtop_item4 = data['info']['participants'][count]['item4']
                redtop_item5 = data['info']['participants'][count]['item5']
                redtop_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                redtop_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                redtop_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                redtop_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                redtop_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                redtop_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                redtop_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                redtop_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                redtop_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                redtop_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                redtop_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                redtop_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                redtop_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5 = get_timeline(region, match_id, api_key, puuid, item_map, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5)
            elif player['teamPosition'] == 'JUNGLE' and player['teamId'] == 100:
                bluejg_id = data['info']['participants'][count]['summonerId']
                bluejg_champ = data['info']['participants'][count]['championName']
                bluejg_kills = data['info']['participants'][count]['kills']
                bluejg_deaths = data['info']['participants'][count]['deaths']
                bluejg_assists = data['info']['participants'][count]['assists']
                bluejg_kda = data['info']['participants'][count]['challenges']['kda']
                bluejg_item0 = data['info']['participants'][count]['item0']
                bluejg_item1 = data['info']['participants'][count]['item1']
                bluejg_item2 = data['info']['participants'][count]['item2']
                bluejg_item3 = data['info']['participants'][count]['item3']
                bluejg_item4 = data['info']['participants'][count]['item4']
                bluejg_item5 = data['info']['participants'][count]['item5']
                bluejg_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                bluejg_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                bluejg_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                bluejg_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                bluejg_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                bluejg_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                bluejg_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                bluejg_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                bluejg_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                bluejg_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                bluejg_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                bluejg_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                bluejg_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5 = get_timeline(region, match_id, api_key, puuid, item_map, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5)
            elif player['teamPosition'] == 'JUNGLE' and player['teamId'] == 200:
                redjg_id = data['info']['participants'][count]['summonerId']
                redjg_champ = data['info']['participants'][count]['championName']
                redjg_kills = data['info']['participants'][count]['kills']
                redjg_deaths = data['info']['participants'][count]['deaths']
                redjg_assists = data['info']['participants'][count]['assists']
                redjg_kda = data['info']['participants'][count]['challenges']['kda']
                redjg_item0 = data['info']['participants'][count]['item0']
                redjg_item1 = data['info']['participants'][count]['item1']
                redjg_item2 = data['info']['participants'][count]['item2']
                redjg_item3 = data['info']['participants'][count]['item3']
                redjg_item4 = data['info']['participants'][count]['item4']
                redjg_item5 = data['info']['participants'][count]['item5']
                redjg_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                redjg_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                redjg_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                redjg_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                redjg_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                redjg_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                redjg_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                redjg_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                redjg_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                redjg_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                redjg_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                redjg_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                redjg_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5 = get_timeline(region, match_id, api_key, puuid, item_map, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5)
            elif player['teamPosition'] == 'MIDDLE' and player['teamId'] == 100:
                bluemid_id = data['info']['participants'][count]['summonerId']
                bluemid_champ = data['info']['participants'][count]['championName']
                bluemid_kills = data['info']['participants'][count]['kills']
                bluemid_deaths = data['info']['participants'][count]['deaths']
                bluemid_assists = data['info']['participants'][count]['assists']
                bluemid_kda = data['info']['participants'][count]['challenges']['kda']
                bluemid_item0 = data['info']['participants'][count]['item0']
                bluemid_item1 = data['info']['participants'][count]['item1']
                bluemid_item2 = data['info']['participants'][count]['item2']
                bluemid_item3 = data['info']['participants'][count]['item3']
                bluemid_item4 = data['info']['participants'][count]['item4']
                bluemid_item5 = data['info']['participants'][count]['item5']
                bluemid_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                bluemid_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                bluemid_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                bluemid_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                bluemid_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                bluemid_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                bluemid_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                bluemid_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                bluemid_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                bluemid_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                bluemid_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                bluemid_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                bluemid_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5 = get_timeline(region, match_id, api_key, puuid, item_map, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5)
            elif player['teamPosition'] == 'MIDDLE' and player['teamId'] == 200:
                redmid_id = data['info']['participants'][count]['summonerId']
                redmid_champ = data['info']['participants'][count]['championName']
                redmid_kills = data['info']['participants'][count]['kills']
                redmid_deaths = data['info']['participants'][count]['deaths']
                redmid_assists = data['info']['participants'][count]['assists']
                redmid_kda = data['info']['participants'][count]['challenges']['kda']
                redmid_item0 = data['info']['participants'][count]['item0']
                redmid_item1 = data['info']['participants'][count]['item1']
                redmid_item2 = data['info']['participants'][count]['item2']
                redmid_item3 = data['info']['participants'][count]['item3']
                redmid_item4 = data['info']['participants'][count]['item4']
                redmid_item5 = data['info']['participants'][count]['item5']
                redmid_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                redmid_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                redmid_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                redmid_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                redmid_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                redmid_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                redmid_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                redmid_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                redmid_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                redmid_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                redmid_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                redmid_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                redmid_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5 = get_timeline(region, match_id, api_key, puuid, item_map, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5)
            elif player['teamPosition'] == 'BOTTOM' and player['teamId'] == 100:
                bluebot_id = data['info']['participants'][count]['summonerId']
                bluebot_champ = data['info']['participants'][count]['championName']
                bluebot_kills = data['info']['participants'][count]['kills']
                bluebot_deaths = data['info']['participants'][count]['deaths']
                bluebot_assists = data['info']['participants'][count]['assists']
                bluebot_kda = data['info']['participants'][count]['challenges']['kda']
                bluebot_item0 = data['info']['participants'][count]['item0']
                bluebot_item1 = data['info']['participants'][count]['item1']
                bluebot_item2 = data['info']['participants'][count]['item2']
                bluebot_item3 = data['info']['participants'][count]['item3']
                bluebot_item4 = data['info']['participants'][count]['item4']
                bluebot_item5 = data['info']['participants'][count]['item5']
                bluebot_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                bluebot_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                bluebot_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                bluebot_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                bluebot_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                bluebot_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                bluebot_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                bluebot_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                bluebot_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                bluebot_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                bluebot_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                bluebot_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                bluebot_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5 = get_timeline(region, match_id, api_key, puuid, item_map, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5)
            elif player['teamPosition'] == 'BOTTOM' and player['teamId'] == 200:
                redbot_id = data['info']['participants'][count]['summonerId']
                redbot_champ = data['info']['participants'][count]['championName']
                redbot_kills = data['info']['participants'][count]['kills']
                redbot_deaths = data['info']['participants'][count]['deaths']
                redbot_assists = data['info']['participants'][count]['assists']
                redbot_kda = data['info']['participants'][count]['challenges']['kda']
                redbot_item0 = data['info']['participants'][count]['item0']
                redbot_item1 = data['info']['participants'][count]['item1']
                redbot_item2 = data['info']['participants'][count]['item2']
                redbot_item3 = data['info']['participants'][count]['item3']
                redbot_item4 = data['info']['participants'][count]['item4']
                redbot_item5 = data['info']['participants'][count]['item5']
                redbot_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                redbot_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                redbot_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                redbot_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                redbot_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                redbot_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                redbot_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                redbot_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                redbot_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                redbot_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                redbot_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                redbot_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                redbot_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5 = get_timeline(region, match_id, api_key, puuid, item_map, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5)
            elif player['teamPosition'] == 'UTILITY' and player['teamId'] == 100:
                bluesup_id = data['info']['participants'][count]['summonerId']
                bluesup_champ = data['info']['participants'][count]['championName']
                bluesup_kills = data['info']['participants'][count]['kills']
                bluesup_deaths = data['info']['participants'][count]['deaths']
                bluesup_assists = data['info']['participants'][count]['assists']
                bluesup_kda = data['info']['participants'][count]['challenges']['kda']
                bluesup_item0 = data['info']['participants'][count]['item0']
                bluesup_item1 = data['info']['participants'][count]['item1']
                bluesup_item2 = data['info']['participants'][count]['item2']
                bluesup_item3 = data['info']['participants'][count]['item3']
                bluesup_item4 = data['info']['participants'][count]['item4']
                bluesup_item5 = data['info']['participants'][count]['item5']
                bluesup_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                bluesup_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                bluesup_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                bluesup_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                bluesup_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                bluesup_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                bluesup_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                bluesup_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                bluesup_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                bluesup_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                bluesup_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                bluesup_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                bluesup_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5 = get_timeline(region, match_id, api_key, puuid, item_map, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5)
            elif player['teamPosition'] == 'UTILITY' and player['teamId'] == 200:
                redsup_id = data['info']['participants'][count]['summonerId']
                redsup_champ = data['info']['participants'][count]['championName']
                redsup_kills = data['info']['participants'][count]['kills']
                redsup_deaths = data['info']['participants'][count]['deaths']
                redsup_assists = data['info']['participants'][count]['assists']
                redsup_kda = data['info']['participants'][count]['challenges']['kda']
                redsup_item0 = data['info']['participants'][count]['item0']
                redsup_item1 = data['info']['participants'][count]['item1']
                redsup_item2 = data['info']['participants'][count]['item2']
                redsup_item3 = data['info']['participants'][count]['item3']
                redsup_item4 = data['info']['participants'][count]['item4']
                redsup_item5 = data['info']['participants'][count]['item5']
                redsup_rune0 = data['info']['participants'][count]['perks']['styles'][0]['selections'][0]['perk']
                redsup_rune1 = data['info']['participants'][count]['perks']['styles'][0]['selections'][1]['perk']
                redsup_rune2 = data['info']['participants'][count]['perks']['styles'][0]['selections'][2]['perk']
                redsup_rune3 = data['info']['participants'][count]['perks']['styles'][0]['selections'][3]['perk']
                redsup_rune4 = data['info']['participants'][count]['perks']['styles'][1]['selections'][0]['perk']
                redsup_rune5 = data['info']['participants'][count]['perks']['styles'][1]['selections'][1]['perk']
                redsup_magicdmgdealt = data['info']['participants'][count]['magicDamageDealtToChampions']
                redsup_physicaldmgdealt = data['info']['participants'][count]['physicalDamageDealtToChampions']
                redsup_truedmgdealt = data['info']['participants'][count]['trueDamageDealtToChampions']
                redsup_ccdealt = data['info']['participants'][count]['totalTimeCCDealt']
                redsup_magicdmgreceive = data['info']['participants'][count]['magicDamageTaken']
                redsup_physicaldmgreceive = data['info']['participants'][count]['physicalDamageTaken']
                redsup_truedmgreceive = data['info']['participants'][count]['trueDamageTaken']
                puuid = data['info']['participants'][count]['puuid']
                redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5 = get_timeline(region, match_id, api_key, puuid, item_map, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5)
            else:
                return None
        except KeyError as e:
            print(f"KeyError encountered: {e}. Skipping match.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}. Skipping match.")
            return None    
    return (timestamp, gameduration, result,
        # Blue Top
        bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_kda, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5, bluetop_magicdmgdealt, bluetop_physicaldmgdealt, bluetop_truedmgdealt, bluetop_ccdealt, bluetop_magicdmgreceive, bluetop_physicaldmgreceive, bluetop_truedmgreceive,
        
        # Blue JG
        bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_kda, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5, bluejg_magicdmgdealt, bluejg_physicaldmgdealt, bluejg_truedmgdealt, bluejg_ccdealt, bluejg_magicdmgreceive, bluejg_physicaldmgreceive, bluejg_truedmgreceive,
        
        # Blue Mid
        bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_kda, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5, bluemid_magicdmgdealt, bluemid_physicaldmgdealt, bluemid_truedmgdealt, bluemid_ccdealt, bluemid_magicdmgreceive, bluemid_physicaldmgreceive, bluemid_truedmgreceive,
        
        # Blue Bot
        bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_kda, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5, bluebot_magicdmgdealt, bluebot_physicaldmgdealt, bluebot_truedmgdealt, bluebot_ccdealt, bluebot_magicdmgreceive, bluebot_physicaldmgreceive, bluebot_truedmgreceive,
        
        # Blue Sup
        bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_kda, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5, bluesup_magicdmgdealt, bluesup_physicaldmgdealt, bluesup_truedmgdealt, bluesup_ccdealt, bluesup_magicdmgreceive, bluesup_physicaldmgreceive, bluesup_truedmgreceive,
        
        # Red Top
        redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_kda, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5, redtop_magicdmgdealt, redtop_physicaldmgdealt, redtop_truedmgdealt, redtop_ccdealt, redtop_magicdmgreceive, redtop_physicaldmgreceive, redtop_truedmgreceive,
        
        # Red JG
        redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_kda, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5, redjg_magicdmgdealt, redjg_physicaldmgdealt, redjg_truedmgdealt, redjg_ccdealt, redjg_magicdmgreceive, redjg_physicaldmgreceive, redjg_truedmgreceive,
        
        # Red Mid
        redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_kda, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5, redmid_magicdmgdealt, redmid_physicaldmgdealt, redmid_truedmgdealt, redmid_ccdealt, redmid_magicdmgreceive, redmid_physicaldmgreceive, redmid_truedmgreceive,
        
        # Red Bot
        redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_kda, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5, redbot_magicdmgdealt, redbot_physicaldmgdealt, redbot_truedmgdealt, redbot_ccdealt, redbot_magicdmgreceive, redbot_physicaldmgreceive, redbot_truedmgreceive,
        
        # Red Sup
        redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_kda, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5, redsup_magicdmgdealt, redsup_physicaldmgdealt, redsup_truedmgdealt, redsup_ccdealt, redsup_magicdmgreceive, redsup_physicaldmgreceive, redsup_truedmgreceive
    )

#inserts data into database
def insert_game(match_code, game_stamp, engine, game_duration, outcome, patch, champion_map,
        # Blue Top
        bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_kda, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5, bluetop_magicdmgdealt, bluetop_physicaldmgdealt, bluetop_truedmgdealt, bluetop_ccdealt, bluetop_magicdmgreceive, bluetop_physicaldmgreceive, bluetop_truedmgreceive,
        
        # Blue JG
        bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_kda, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5, bluejg_magicdmgdealt, bluejg_physicaldmgdealt, bluejg_truedmgdealt, bluejg_ccdealt, bluejg_magicdmgreceive, bluejg_physicaldmgreceive, bluejg_truedmgreceive,
        
        # Blue Mid
        bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_kda, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5, bluemid_magicdmgdealt, bluemid_physicaldmgdealt, bluemid_truedmgdealt, bluemid_ccdealt, bluemid_magicdmgreceive, bluemid_physicaldmgreceive, bluemid_truedmgreceive,
        
        # Blue Bot
        bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_kda, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5, bluebot_magicdmgdealt, bluebot_physicaldmgdealt, bluebot_truedmgdealt, bluebot_ccdealt, bluebot_magicdmgreceive, bluebot_physicaldmgreceive, bluebot_truedmgreceive,
        
        # Blue Sup
        bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_kda, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5, bluesup_magicdmgdealt, bluesup_physicaldmgdealt, bluesup_truedmgdealt, bluesup_ccdealt, bluesup_magicdmgreceive, bluesup_physicaldmgreceive, bluesup_truedmgreceive,
        
        # Red Top
        redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_kda, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5, redtop_magicdmgdealt, redtop_physicaldmgdealt, redtop_truedmgdealt, redtop_ccdealt, redtop_magicdmgreceive, redtop_physicaldmgreceive, redtop_truedmgreceive,
        
        # Red JG
        redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_kda, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5, redjg_magicdmgdealt, redjg_physicaldmgdealt, redjg_truedmgdealt, redjg_ccdealt, redjg_magicdmgreceive, redjg_physicaldmgreceive, redjg_truedmgreceive,
        
        # Red Mid
        redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_kda, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5, redmid_magicdmgdealt, redmid_physicaldmgdealt, redmid_truedmgdealt, redmid_ccdealt, redmid_magicdmgreceive, redmid_physicaldmgreceive, redmid_truedmgreceive,
        
        # Red Bot
        redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_kda, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5, redbot_magicdmgdealt, redbot_physicaldmgdealt, redbot_truedmgdealt, redbot_ccdealt, redbot_magicdmgreceive, redbot_physicaldmgreceive, redbot_truedmgreceive,
        
        # Red Sup
        redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_kda, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5, redsup_magicdmgdealt, redsup_physicaldmgdealt, redsup_truedmgdealt, redsup_ccdealt, redsup_magicdmgreceive, redsup_physicaldmgreceive, redsup_truedmgreceive
    ):
        check_sql = """
        SELECT * FROM highelo_matches
        WHERE match_code = :match_code
        """
        with engine.begin() as connection:
            result = connection.execute(text(check_sql), {
                "match_code": match_code
            })
            row = result.fetchone()
            if row:
                print("Duplicate")
                return
            else:
                connection.execute(text(""" 
                        INSERT INTO highelo_matches(
                            match_code, game_stamp, game_duration, result, patch,
                            bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_kda, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5, bluetop_magicdmgdealt, bluetop_physicaldmgdealt, bluetop_truedmgdealt, bluetop_ccdealt, bluetop_magicdmgreceive, bluetop_physicaldmgreceive, bluetop_truedmgreceive,
                            bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_kda, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5, bluejg_magicdmgdealt, bluejg_physicaldmgdealt, bluejg_truedmgdealt, bluejg_ccdealt, bluejg_magicdmgreceive, bluejg_physicaldmgreceive, bluejg_truedmgreceive,
                            bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_kda, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5, bluemid_magicdmgdealt, bluemid_physicaldmgdealt, bluemid_truedmgdealt, bluemid_ccdealt, bluemid_magicdmgreceive, bluemid_physicaldmgreceive, bluemid_truedmgreceive,
                            bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_kda, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5, bluebot_magicdmgdealt, bluebot_physicaldmgdealt, bluebot_truedmgdealt, bluebot_ccdealt, bluebot_magicdmgreceive, bluebot_physicaldmgreceive, bluebot_truedmgreceive,
                            bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_kda, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5, bluesup_magicdmgdealt, bluesup_physicaldmgdealt, bluesup_truedmgdealt, bluesup_ccdealt, bluesup_magicdmgreceive, bluesup_physicaldmgreceive, bluesup_truedmgreceive,
                            redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_kda, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5, redtop_magicdmgdealt, redtop_physicaldmgdealt, redtop_truedmgdealt, redtop_ccdealt, redtop_magicdmgreceive, redtop_physicaldmgreceive, redtop_truedmgreceive,
                            redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_kda, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5, redjg_magicdmgdealt, redjg_physicaldmgdealt, redjg_truedmgdealt, redjg_ccdealt, redjg_magicdmgreceive, redjg_physicaldmgreceive, redjg_truedmgreceive,
                            redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_kda, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5, redmid_magicdmgdealt, redmid_physicaldmgdealt, redmid_truedmgdealt, redmid_ccdealt, redmid_magicdmgreceive, redmid_physicaldmgreceive, redmid_truedmgreceive,
                            redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_kda, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5, redbot_magicdmgdealt, redbot_physicaldmgdealt, redbot_truedmgdealt, redbot_ccdealt, redbot_magicdmgreceive, redbot_physicaldmgreceive, redbot_truedmgreceive,
                            redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_kda, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5, redsup_magicdmgdealt, redsup_physicaldmgdealt, redsup_truedmgdealt, redsup_ccdealt, redsup_magicdmgreceive, redsup_physicaldmgreceive, redsup_truedmgreceive
                        ) VALUES (
                            :match_code, :game_stamp, :game_duration, :result, :patch,
                            :bluetop_id, :bluetop_champ, :bluetop_kills, :bluetop_deaths, :bluetop_assists, :bluetop_kda, :bluetop_item0, :bluetop_item1, :bluetop_item2, :bluetop_item3, :bluetop_item4, :bluetop_item5, :bluetop_rune0, :bluetop_rune1, :bluetop_rune2, :bluetop_rune3, :bluetop_rune4, :bluetop_rune5, :bluetop_magicdmgdealt, :bluetop_physicaldmgdealt, :bluetop_truedmgdealt, :bluetop_ccdealt, :bluetop_magicdmgreceive, :bluetop_physicaldmgreceive, :bluetop_truedmgreceive,
                            :bluejg_id, :bluejg_champ, :bluejg_kills, :bluejg_deaths, :bluejg_assists, :bluejg_kda, :bluejg_item0, :bluejg_item1, :bluejg_item2, :bluejg_item3, :bluejg_item4, :bluejg_item5, :bluejg_rune0, :bluejg_rune1, :bluejg_rune2, :bluejg_rune3, :bluejg_rune4, :bluejg_rune5, :bluejg_magicdmgdealt, :bluejg_physicaldmgdealt, :bluejg_truedmgdealt, :bluejg_ccdealt, :bluejg_magicdmgreceive, :bluejg_physicaldmgreceive, :bluejg_truedmgreceive,
                            :bluemid_id, :bluemid_champ, :bluemid_kills, :bluemid_deaths, :bluemid_assists, :bluemid_kda, :bluemid_item0, :bluemid_item1, :bluemid_item2, :bluemid_item3, :bluemid_item4, :bluemid_item5, :bluemid_rune0, :bluemid_rune1, :bluemid_rune2, :bluemid_rune3, :bluemid_rune4, :bluemid_rune5, :bluemid_magicdmgdealt, :bluemid_physicaldmgdealt, :bluemid_truedmgdealt, :bluemid_ccdealt, :bluemid_magicdmgreceive, :bluemid_physicaldmgreceive, :bluemid_truedmgreceive,
                            :bluebot_id, :bluebot_champ, :bluebot_kills, :bluebot_deaths, :bluebot_assists, :bluebot_kda, :bluebot_item0, :bluebot_item1, :bluebot_item2, :bluebot_item3, :bluebot_item4, :bluebot_item5, :bluebot_rune0, :bluebot_rune1, :bluebot_rune2, :bluebot_rune3, :bluebot_rune4, :bluebot_rune5, :bluebot_magicdmgdealt, :bluebot_physicaldmgdealt, :bluebot_truedmgdealt, :bluebot_ccdealt, :bluebot_magicdmgreceive, :bluebot_physicaldmgreceive, :bluebot_truedmgreceive,
                            :bluesup_id, :bluesup_champ, :bluesup_kills, :bluesup_deaths, :bluesup_assists, :bluesup_kda, :bluesup_item0, :bluesup_item1, :bluesup_item2, :bluesup_item3, :bluesup_item4, :bluesup_item5, :bluesup_rune0, :bluesup_rune1, :bluesup_rune2, :bluesup_rune3, :bluesup_rune4, :bluesup_rune5, :bluesup_magicdmgdealt, :bluesup_physicaldmgdealt, :bluesup_truedmgdealt, :bluesup_ccdealt, :bluesup_magicdmgreceive, :bluesup_physicaldmgreceive, :bluesup_truedmgreceive,
                            :redtop_id, :redtop_champ, :redtop_kills, :redtop_deaths, :redtop_assists, :redtop_kda, :redtop_item0, :redtop_item1, :redtop_item2, :redtop_item3, :redtop_item4, :redtop_item5, :redtop_rune0, :redtop_rune1, :redtop_rune2, :redtop_rune3, :redtop_rune4, :redtop_rune5, :redtop_magicdmgdealt, :redtop_physicaldmgdealt, :redtop_truedmgdealt, :redtop_ccdealt, :redtop_magicdmgreceive, :redtop_physicaldmgreceive, :redtop_truedmgreceive,
                            :redjg_id, :redjg_champ, :redjg_kills, :redjg_deaths, :redjg_assists, :redjg_kda, :redjg_item0, :redjg_item1, :redjg_item2, :redjg_item3, :redjg_item4, :redjg_item5, :redjg_rune0, :redjg_rune1, :redjg_rune2, :redjg_rune3, :redjg_rune4, :redjg_rune5, :redjg_magicdmgdealt, :redjg_physicaldmgdealt, :redjg_truedmgdealt, :redjg_ccdealt, :redjg_magicdmgreceive, :redjg_physicaldmgreceive, :redjg_truedmgreceive,
                            :redmid_id, :redmid_champ, :redmid_kills, :redmid_deaths, :redmid_assists, :redmid_kda, :redmid_item0, :redmid_item1, :redmid_item2, :redmid_item3, :redmid_item4, :redmid_item5, :redmid_rune0, :redmid_rune1, :redmid_rune2, :redmid_rune3, :redmid_rune4, :redmid_rune5, :redmid_magicdmgdealt, :redmid_physicaldmgdealt, :redmid_truedmgdealt, :redmid_ccdealt, :redmid_magicdmgreceive, :redmid_physicaldmgreceive, :redmid_truedmgreceive,
                            :redbot_id, :redbot_champ, :redbot_kills, :redbot_deaths, :redbot_assists, :redbot_kda, :redbot_item0, :redbot_item1, :redbot_item2, :redbot_item3, :redbot_item4, :redbot_item5, :redbot_rune0, :redbot_rune1, :redbot_rune2, :redbot_rune3, :redbot_rune4, :redbot_rune5, :redbot_magicdmgdealt, :redbot_physicaldmgdealt, :redbot_truedmgdealt, :redbot_ccdealt, :redbot_magicdmgreceive, :redbot_physicaldmgreceive, :redbot_truedmgreceive,
                            :redsup_id, :redsup_champ, :redsup_kills, :redsup_deaths, :redsup_assists, :redbot_kda, :redsup_item0, :redsup_item1, :redsup_item2, :redsup_item3, :redsup_item4, :redsup_item5, :redsup_rune0, :redsup_rune1, :redsup_rune2, :redsup_rune3, :redsup_rune4, :redsup_rune5, :redsup_magicdmgdealt, :redsup_physicaldmgdealt, :redsup_truedmgdealt, :redsup_ccdealt, :redsup_magicdmgreceive, :redsup_physicaldmgreceive, :redsup_truedmgreceive
                        )
                    """
                ), {
                    "match_code": match_code, "game_stamp": game_stamp, "game_duration": game_duration, "result": outcome, "patch": patch,
                    "bluetop_id": bluetop_id, "bluetop_champ": champion_map[bluetop_champ], "bluetop_kills": bluetop_kills, "bluetop_deaths": bluetop_deaths, "bluetop_assists": bluetop_assists, "bluetop_kda": bluetop_kda, "bluetop_item0": bluetop_item0, "bluetop_item1": bluetop_item1, 
                    "bluetop_item2": bluetop_item2, "bluetop_item3": bluetop_item3, "bluetop_item4": bluetop_item4, "bluetop_item5": bluetop_item5, 
                    "bluetop_rune0": bluetop_rune0, "bluetop_rune1": bluetop_rune1, "bluetop_rune2": bluetop_rune2, "bluetop_rune3": bluetop_rune3,
                    "bluetop_rune4": bluetop_rune4, "bluetop_rune5": bluetop_rune5, "bluetop_magicdmgdealt": bluetop_magicdmgdealt, "bluetop_physicaldmgdealt": bluetop_physicaldmgdealt, "bluetop_truedmgdealt": bluetop_truedmgdealt, "bluetop_ccdealt": bluetop_ccdealt, "bluetop_magicdmgreceive": bluetop_magicdmgreceive, "bluetop_physicaldmgreceive": bluetop_physicaldmgreceive, "bluetop_truedmgreceive": bluetop_truedmgreceive, 
                    "redtop_id": redtop_id, "redtop_champ": champion_map[redtop_champ], "redtop_kills": redtop_kills, "redtop_deaths": redtop_deaths, "redtop_assists": redtop_assists, "redtop_kda": redtop_kda, "redtop_item0": redtop_item0, "redtop_item1": redtop_item1, 
                    "redtop_item2": redtop_item2, "redtop_item3": redtop_item3, "redtop_item4": redtop_item4, "redtop_item5": redtop_item5, 
                    "redtop_rune0": redtop_rune0, "redtop_rune1": redtop_rune1, "redtop_rune2": redtop_rune2, "redtop_rune3": redtop_rune3, 
                    "redtop_rune4": redtop_rune4, "redtop_rune5": redtop_rune5, "redtop_magicdmgdealt": redtop_magicdmgdealt, "redtop_physicaldmgdealt": redtop_physicaldmgdealt, "redtop_truedmgdealt": redtop_truedmgdealt, "redtop_ccdealt": redtop_ccdealt, "redtop_magicdmgreceive": redtop_magicdmgreceive, "redtop_physicaldmgreceive": redtop_physicaldmgreceive, "redtop_truedmgreceive": redtop_truedmgreceive,
                    "bluejg_id": bluejg_id, "bluejg_champ": champion_map[bluejg_champ], "bluejg_kills": bluejg_kills, "bluejg_deaths": bluejg_deaths, "bluejg_assists": bluejg_assists, "bluejg_kda": bluejg_kda,"bluejg_item0": bluejg_item0, "bluejg_item1": bluejg_item1, 
                    "bluejg_item2": bluejg_item2, "bluejg_item3": bluejg_item3, "bluejg_item4": bluejg_item4, "bluejg_item5": bluejg_item5, 
                    "bluejg_rune0": bluejg_rune0, "bluejg_rune1": bluejg_rune1, "bluejg_rune2": bluejg_rune2, "bluejg_rune3": bluejg_rune3, 
                    "bluejg_rune4": bluejg_rune4, "bluejg_rune5": bluejg_rune5, "bluejg_magicdmgdealt": bluejg_magicdmgdealt, "bluejg_physicaldmgdealt": bluejg_physicaldmgdealt, "bluejg_truedmgdealt": bluejg_truedmgdealt, "bluejg_ccdealt": bluejg_ccdealt, "bluejg_magicdmgreceive": bluejg_magicdmgreceive, "bluejg_physicaldmgreceive": bluejg_physicaldmgreceive, "bluejg_truedmgreceive": bluejg_truedmgreceive,
                    "redjg_id": redjg_id, "redjg_champ": champion_map[redjg_champ], "redjg_kills": redjg_kills, "redjg_deaths": redjg_deaths, "redjg_assists": redjg_assists, "redjg_kda": redjg_kda,"redjg_item0": redjg_item0, "redjg_item1": redjg_item1, 
                    "redjg_item2": redjg_item2, "redjg_item3": redjg_item3, "redjg_item4": redjg_item4, "redjg_item5": redjg_item5, 
                    "redjg_rune0": redjg_rune0, "redjg_rune1": redjg_rune1, "redjg_rune2": redjg_rune2, "redjg_rune3": redjg_rune3, 
                    "redjg_rune4": redjg_rune4, "redjg_rune5": redjg_rune5, "redjg_magicdmgdealt": redjg_magicdmgdealt, "redjg_physicaldmgdealt": redjg_physicaldmgdealt, "redjg_truedmgdealt": redjg_truedmgdealt, "redjg_ccdealt": redjg_ccdealt, "redjg_magicdmgreceive": redjg_magicdmgreceive, "redjg_physicaldmgreceive": redjg_physicaldmgreceive, "redjg_truedmgreceive": redjg_truedmgreceive,
                    "bluemid_id": bluemid_id, "bluemid_champ": champion_map[bluemid_champ], "bluemid_kills": bluemid_kills, "bluemid_deaths": bluemid_deaths, "bluemid_assists": bluemid_assists, "bluemid_kda": bluemid_kda, "bluemid_item0": bluemid_item0, "bluemid_item1": bluemid_item1, 
                    "bluemid_item2": bluemid_item2, "bluemid_item3": bluemid_item3, "bluemid_item4": bluemid_item4, "bluemid_item5": bluemid_item5, 
                    "bluemid_rune0": bluemid_rune0, "bluemid_rune1": bluemid_rune1, "bluemid_rune2": bluemid_rune2, "bluemid_rune3": bluemid_rune3, 
                    "bluemid_rune4": bluemid_rune4, "bluemid_rune5": bluemid_rune5, "bluemid_magicdmgdealt": bluemid_magicdmgdealt, "bluemid_physicaldmgdealt": bluemid_physicaldmgdealt, "bluemid_truedmgdealt": bluemid_truedmgdealt, "bluemid_ccdealt": bluemid_ccdealt, "bluemid_magicdmgreceive": bluemid_magicdmgreceive, "bluemid_physicaldmgreceive": bluemid_physicaldmgreceive, "bluemid_truedmgreceive": bluemid_truedmgreceive,
                    "redmid_id": redmid_id, "redmid_champ": champion_map[redmid_champ], "redmid_kills": redmid_kills, "redmid_deaths": redmid_deaths, "redmid_assists": redmid_assists, "redmid_kda": redmid_kda, "redmid_item0": redmid_item0, "redmid_item1": redmid_item1, 
                    "redmid_item2": redmid_item2, "redmid_item3": redmid_item3, "redmid_item4": redmid_item4, "redmid_item5": redmid_item5, 
                    "redmid_rune0": redmid_rune0, "redmid_rune1": redmid_rune1, "redmid_rune2": redmid_rune2, "redmid_rune3": redmid_rune3, 
                    "redmid_rune4": redmid_rune4, "redmid_rune5": redmid_rune5, "redmid_magicdmgdealt": redmid_magicdmgdealt, "redmid_physicaldmgdealt": redmid_physicaldmgdealt, "redmid_truedmgdealt": redmid_truedmgdealt, "redmid_ccdealt": redmid_ccdealt, "redmid_magicdmgreceive": redmid_magicdmgreceive, "redmid_physicaldmgreceive": redmid_physicaldmgreceive, "redmid_truedmgreceive": redmid_truedmgreceive,
                    "bluebot_id": bluebot_id, "bluebot_champ": champion_map[bluebot_champ], "bluebot_kills": bluebot_kills, "bluebot_deaths": bluebot_deaths, "bluebot_assists": bluebot_assists, "bluebot_kda": bluebot_kda, "bluebot_item0": bluebot_item0, "bluebot_item1": bluebot_item1, 
                    "bluebot_item2": bluebot_item2, "bluebot_item3": bluebot_item3, "bluebot_item4": bluebot_item4, "bluebot_item5": bluebot_item5, 
                    "bluebot_rune0": bluebot_rune0, "bluebot_rune1": bluebot_rune1, "bluebot_rune2": bluebot_rune2, "bluebot_rune3": bluebot_rune3, 
                    "bluebot_rune4": bluebot_rune4, "bluebot_rune5": bluebot_rune5, "bluebot_magicdmgdealt": bluebot_magicdmgdealt, "bluebot_physicaldmgdealt": bluebot_physicaldmgdealt, "bluebot_truedmgdealt": bluebot_truedmgdealt, "bluebot_ccdealt": bluebot_ccdealt, "bluebot_magicdmgreceive": bluebot_magicdmgreceive, "bluebot_physicaldmgreceive": bluebot_physicaldmgreceive, "bluebot_truedmgreceive": bluebot_truedmgreceive,
                    "redbot_id": redbot_id, "redbot_champ": champion_map[redbot_champ], "redbot_kills": redbot_kills, "redbot_deaths": redbot_deaths, "redbot_assists": redbot_assists, "redbot_kda": redbot_kda, "redbot_item0": redbot_item0, "redbot_item1": redbot_item1, 
                    "redbot_item2": redbot_item2, "redbot_item3": redbot_item3, "redbot_item4": redbot_item4, "redbot_item5": redbot_item5, 
                    "redbot_rune0": redbot_rune0, "redbot_rune1": redbot_rune1, "redbot_rune2": redbot_rune2, "redbot_rune3": redbot_rune3, 
                    "redbot_rune4": redbot_rune4, "redbot_rune5": redbot_rune5, "redbot_magicdmgdealt": redbot_magicdmgdealt, "redbot_physicaldmgdealt": redbot_physicaldmgdealt, "redbot_truedmgdealt": redbot_truedmgdealt, "redbot_ccdealt": redbot_ccdealt, "redbot_magicdmgreceive": redbot_magicdmgreceive, "redbot_physicaldmgreceive": redbot_physicaldmgreceive, "redbot_truedmgreceive": redbot_truedmgreceive,
                    "bluesup_id": bluesup_id, "bluesup_champ": champion_map[bluesup_champ], "bluesup_kills": bluesup_kills, "bluesup_deaths": bluesup_deaths, "bluesup_assists": bluesup_assists, "bluesup_kda": bluesup_kda, "bluesup_item0": bluesup_item0, "bluesup_item1": bluesup_item1, 
                    "bluesup_item2": bluesup_item2, "bluesup_item3": bluesup_item3, "bluesup_item4": bluesup_item4, "bluesup_item5": bluesup_item5, 
                    "bluesup_rune0": bluesup_rune0, "bluesup_rune1": bluesup_rune1, "bluesup_rune2": bluesup_rune2, "bluesup_rune3": bluesup_rune3, 
                    "bluesup_rune4": bluesup_rune4, "bluesup_rune5": bluesup_rune5, "bluesup_magicdmgdealt": bluesup_magicdmgdealt, "bluesup_physicaldmgdealt": bluesup_physicaldmgdealt, "bluesup_truedmgdealt": bluesup_truedmgdealt, "bluesup_ccdealt": bluesup_ccdealt, "bluesup_magicdmgreceive": bluesup_magicdmgreceive, "bluesup_physicaldmgreceive": bluesup_physicaldmgreceive, "bluesup_truedmgreceive": bluesup_truedmgreceive,
                    "redsup_id": redsup_id, "redsup_champ": champion_map[redsup_champ], "redsup_kills": redsup_kills, "redsup_deaths": redsup_deaths, "redsup_assists": redsup_assists, "redsup_kda": redsup_kda, "redsup_item0": redsup_item0, "redsup_item1": redsup_item1, 
                    "redsup_item2": redsup_item2, "redsup_item3": redsup_item3, "redsup_item4": redsup_item4, "redsup_item5": redsup_item5, 
                    "redsup_rune0": redsup_rune0, "redsup_rune1": redsup_rune1, "redsup_rune2": redsup_rune2, "redsup_rune3": redsup_rune3, 
                    "redsup_rune4": redsup_rune4, "redsup_rune5": redsup_rune5, "redsup_magicdmgdealt": redsup_magicdmgdealt, "redsup_physicaldmgdealt": redsup_physicaldmgdealt, "redsup_truedmgdealt": redsup_truedmgdealt, "redsup_ccdealt": redsup_ccdealt, "redsup_magicdmgreceive": redsup_magicdmgreceive, "redsup_physicaldmgreceive": redsup_physicaldmgreceive, "redsup_truedmgreceive": redsup_truedmgreceive 
                })

#fetches user from database
def fetch_id():
    check_sql = """
    SELECT * FROM highelo_player
    """
    with engine.begin() as connection:
            result = connection.execute(text(check_sql))
            row = result.fetchall()
            if row:
                return row

#fetches current patch
def fetch_patch():
    patch_url = f'https://ddragon.leagueoflegends.com/api/versions.json'
    response = requests.get(patch_url)
    data = response.json()
    return data[0]


if __name__ == '__main__':
    api_key = get_json("API_KEY") #Fetches api key
    engine = establish_connection() #establishes connection to database
    patch = fetch_patch()
    region_list = ['BR1', 'EUW1', 'EUN1', 'JP1', 'KR', 'LA1', 'LA2', 'ME1', 'NA1', 'OC1', 'PH2', 'RU', 'SG2', 'TH2', 'TR1', 'TW2', 'VN2']
    test_list = ['NA1']
    rank_list = ['Challenger', 'Grandmaster', 'Master']
    item_map = fetch_item(patch)
    rune_map = fetch_rune(patch)
    champion_map = champ_map(patch)
    #Updates player base
    for region in test_list:
        for rank in rank_list:
            if rank == 'Challenger':
                players = fetch_challenger(region, api_key)
            elif rank == 'Grandmaster':
                players = fetch_grandmaster(region, api_key)
            else:
                players = fetch_master(region, api_key)
            update_players(players, engine, region, api_key, rank)
            print("Updated high elo player base")
            for player in fetch_id():
                last_updated = int(player[10].timestamp())
                all_matches = fetch_matches(region, player[2], api_key, last_updated)
                insert_player(engine, player[1], player[2], player[3], player[4], player[5], player[6], player[7], player[8], player[9], datetime.now())
                print("Fetching matches since last update")
                for match in all_matches:
                    print("Fetching match data") 
                    details = fetch_match_data(match, api_key, region)
                    if details is not None:
                        (time_stamp, game_duration, result,
                            # Blue Top
                            bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_kda, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5, bluetop_magicdmgdealt, bluetop_physicaldmgdealt, bluetop_truedmgdealt, bluetop_ccdealt, bluetop_magicdmgreceive, bluetop_physicaldmgreceive, bluetop_truedmgreceive,
                            
                            # Blue JG
                            bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_kda, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5, bluejg_magicdmgdealt, bluejg_physicaldmgdealt, bluejg_truedmgdealt, bluejg_ccdealt, bluejg_magicdmgreceive, bluejg_physicaldmgreceive, bluejg_truedmgreceive,
                            
                            # Blue Mid
                            bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_kda, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5, bluemid_magicdmgdealt, bluemid_physicaldmgdealt, bluemid_truedmgdealt, bluemid_ccdealt, bluemid_magicdmgreceive, bluemid_physicaldmgreceive, bluemid_truedmgreceive,
                            
                            # Blue Bot
                            bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_kda, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5, bluebot_magicdmgdealt, bluebot_physicaldmgdealt, bluebot_truedmgdealt, bluebot_ccdealt, bluebot_magicdmgreceive, bluebot_physicaldmgreceive, bluebot_truedmgreceive,
                            
                            # Blue Sup
                            bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_kda, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5, bluesup_magicdmgdealt, bluesup_physicaldmgdealt, bluesup_truedmgdealt, bluesup_ccdealt, bluesup_magicdmgreceive, bluesup_physicaldmgreceive, bluesup_truedmgreceive,
                            
                            # Red Top
                            redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_kda, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5, redtop_magicdmgdealt, redtop_physicaldmgdealt, redtop_truedmgdealt, redtop_ccdealt, redtop_magicdmgreceive, redtop_physicaldmgreceive, redtop_truedmgreceive,
                            
                            # Red JG
                            redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_kda, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5, redjg_magicdmgdealt, redjg_physicaldmgdealt, redjg_truedmgdealt, redjg_ccdealt, redjg_magicdmgreceive, redjg_physicaldmgreceive, redjg_truedmgreceive,
                            
                            # Red Mid
                            redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_kda, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5, redmid_magicdmgdealt, redmid_physicaldmgdealt, redmid_truedmgdealt, redmid_ccdealt, redmid_magicdmgreceive, redmid_physicaldmgreceive, redmid_truedmgreceive,
                            
                            # Red Bot
                            redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_kda, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5, redbot_magicdmgdealt, redbot_physicaldmgdealt, redbot_truedmgdealt, redbot_ccdealt, redbot_magicdmgreceive, redbot_physicaldmgreceive, redbot_truedmgreceive,
                            
                            # Red Sup
                            redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_kda, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5, redsup_magicdmgdealt, redsup_physicaldmgdealt, redsup_truedmgdealt, redsup_ccdealt, redsup_magicdmgreceive, redsup_physicaldmgreceive, redsup_truedmgreceive
                        ) = details
                        time.sleep(5)
                        print("Inserting the game")
                        insert_game(match, time_stamp, engine, game_duration, result, patch, champion_map, 
                            # Blue Top
                            bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_kda, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5, bluetop_magicdmgdealt, bluetop_physicaldmgdealt, bluetop_truedmgdealt, bluetop_ccdealt, bluetop_magicdmgreceive, bluetop_physicaldmgreceive, bluetop_truedmgreceive,
                            
                            # Blue JG
                            bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_kda, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5, bluejg_magicdmgdealt, bluejg_physicaldmgdealt, bluejg_truedmgdealt, bluejg_ccdealt, bluejg_magicdmgreceive, bluejg_physicaldmgreceive, bluejg_truedmgreceive,
                            
                            # Blue Mid
                            bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_kda, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5, bluemid_magicdmgdealt, bluemid_physicaldmgdealt, bluemid_truedmgdealt, bluemid_ccdealt, bluemid_magicdmgreceive, bluemid_physicaldmgreceive, bluemid_truedmgreceive,
                            
                            # Blue Bot
                            bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_kda, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5, bluebot_magicdmgdealt, bluebot_physicaldmgdealt, bluebot_truedmgdealt, bluebot_ccdealt, bluebot_magicdmgreceive, bluebot_physicaldmgreceive, bluebot_truedmgreceive,
                            
                            # Blue Sup
                            bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_kda, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5, bluesup_magicdmgdealt, bluesup_physicaldmgdealt, bluesup_truedmgdealt, bluesup_ccdealt, bluesup_magicdmgreceive, bluesup_physicaldmgreceive, bluesup_truedmgreceive,
                            
                            # Red Top
                            redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_kda, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5, redtop_magicdmgdealt, redtop_physicaldmgdealt, redtop_truedmgdealt, redtop_ccdealt, redtop_magicdmgreceive, redtop_physicaldmgreceive, redtop_truedmgreceive,
                            
                            # Red JG
                            redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_kda, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5, redjg_magicdmgdealt, redjg_physicaldmgdealt, redjg_truedmgdealt, redjg_ccdealt, redjg_magicdmgreceive, redjg_physicaldmgreceive, redjg_truedmgreceive,
                            
                            # Red Mid
                            redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_kda, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5, redmid_magicdmgdealt, redmid_physicaldmgdealt, redmid_truedmgdealt, redmid_ccdealt, redmid_magicdmgreceive, redmid_physicaldmgreceive, redmid_truedmgreceive,
                            
                            # Red Bot
                            redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_kda, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5, redbot_magicdmgdealt, redbot_physicaldmgdealt, redbot_truedmgdealt, redbot_ccdealt, redbot_magicdmgreceive, redbot_physicaldmgreceive, redbot_truedmgreceive,
                            
                            # Red Sup
                            redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_kda, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5, redsup_magicdmgdealt, redsup_physicaldmgdealt, redsup_truedmgdealt, redsup_ccdealt, redsup_magicdmgreceive, redsup_physicaldmgreceive, redsup_truedmgreceive
                        )
                    print("Inserted game into database")


            