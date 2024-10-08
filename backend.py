import os
import json
import requests
import pytz
import datetime
from sqlalchemy import create_engine, text
from datetime import datetime
import time

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

    item_mapping = {int(item_id): item_info['name'] for item_id, item_info in item_data['data'].items()}

    item_mapping[0] = 'None'
    return item_mapping

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
    return response.json()

#fetches grandmaster players
def fetch_grandmaster(region, api_key):
    grandmaster_link = f'https://{region}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(grandmaster_link)
    print("Fetching Grandmaster Players")
    print(response.status_code)
    return response.json()

#fetches master players
def fetch_master(region, api_key):
    master_link = f'https://{region}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(master_link)
    print("Fetching Mater Players")
    print(response.status_code)
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
        if player['teamPosition'] == 'TOP' and player['teamId'] == 100:
            bluetop_id = data['info']['participants'][count]['summonerId']
            bluetop_champ = data['info']['participants'][count]['championName']
            bluetop_kills = data['info']['participants'][count]['kills']
            bluetop_deaths = data['info']['participants'][count]['deaths']
            bluetop_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'TOP' and player['teamId'] == 200:
            redtop_id = data['info']['participants'][count]['summonerId']
            redtop_champ = data['info']['participants'][count]['championName']
            redtop_kills = data['info']['participants'][count]['kills']
            redtop_deaths = data['info']['participants'][count]['deaths']
            redtop_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'JUNGLE' and player['teamId'] == 100:
            bluejg_id = data['info']['participants'][count]['summonerId']
            bluejg_champ = data['info']['participants'][count]['championName']
            bluejg_kills = data['info']['participants'][count]['kills']
            bluejg_deaths = data['info']['participants'][count]['deaths']
            bluejg_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'JUNGLE' and player['teamId'] == 200:
            redjg_id = data['info']['participants'][count]['summonerId']
            redjg_champ = data['info']['participants'][count]['championName']
            redjg_kills = data['info']['participants'][count]['kills']
            redjg_deaths = data['info']['participants'][count]['deaths']
            redjg_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'MIDDLE' and player['teamId'] == 100:
            bluemid_id = data['info']['participants'][count]['summonerId']
            bluemid_champ = data['info']['participants'][count]['championName']
            bluemid_kills = data['info']['participants'][count]['kills']
            bluemid_deaths = data['info']['participants'][count]['deaths']
            bluemid_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'MIDDLE' and player['teamId'] == 200:
            redmid_id = data['info']['participants'][count]['summonerId']
            redmid_champ = data['info']['participants'][count]['championName']
            redmid_kills = data['info']['participants'][count]['kills']
            redmid_deaths = data['info']['participants'][count]['deaths']
            redmid_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'BOTTOM' and player['teamId'] == 100:
            bluebot_id = data['info']['participants'][count]['summonerId']
            bluebot_champ = data['info']['participants'][count]['championName']
            bluebot_kills = data['info']['participants'][count]['kills']
            bluebot_deaths = data['info']['participants'][count]['deaths']
            bluebot_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'BOTTOM' and player['teamId'] == 200:
            redbot_id = data['info']['participants'][count]['summonerId']
            redbot_champ = data['info']['participants'][count]['championName']
            redbot_kills = data['info']['participants'][count]['kills']
            redbot_deaths = data['info']['participants'][count]['deaths']
            redbot_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'UTILITY' and player['teamId'] == 100:
            bluesup_id = data['info']['participants'][count]['summonerId']
            bluesup_champ = data['info']['participants'][count]['championName']
            bluesup_kills = data['info']['participants'][count]['kills']
            bluesup_deaths = data['info']['participants'][count]['deaths']
            bluesup_assists = data['info']['participants'][count]['assists']
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
        elif player['teamPosition'] == 'UTILITY' and player['teamId'] == 200:
            redsup_id = data['info']['participants'][count]['summonerId']
            redsup_champ = data['info']['participants'][count]['championName']
            redsup_kills = data['info']['participants'][count]['kills']
            redsup_deaths = data['info']['participants'][count]['deaths']
            redsup_assists = data['info']['participants'][count]['assists']
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
    return (timestamp, gameduration, result,
        # Blue Top
        bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5,
        
        # Blue JG
        bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5,
        
        # Blue Mid
        bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5,
        
        # Blue Bot
        bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5,
        
        # Blue Sup
        bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5,
        
        # Red Top
        redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5,
        
        # Red JG
        redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5,
        
        # Red Mid
        redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5,
        
        # Red Bot
        redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5,
        
        # Red Sup
        redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5
    )

#inserts data into database
def insert_game(match_code, game_stamp, engine, game_duration, outcome, patch,
        # Blue Top
        bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5,
        
        # Blue JG
        bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5,
        
        # Blue Mid
        bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5,
        
        # Blue Bot
        bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5,
        
        # Blue Sup
        bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5,
        
        # Red Top
        redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5,
        
        # Red JG
        redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5,
        
        # Red Mid
        redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5,
        
        # Red Bot
        redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5,
        
        # Red Sup
        redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5
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
                    bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, 
                    bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5, 
                    redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, 
                    redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5, 
                    bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, 
                    bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5, 
                    redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, 
                    redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5, 
                    bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, 
                    bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5, 
                    redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, 
                    redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5, 
                    bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, 
                    bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5, 
                    redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, 
                    redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5, 
                    bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, 
                    bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5, 
                    redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, 
                    redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5
                ) 
                VALUES (
                    :match_code, :game_stamp, :game_duration, :result, :patch, 
                    :bluetop_id, :bluetop_champ, :bluetop_kills, :bluetop_deaths, :bluetop_assists, :bluetop_item0, :bluetop_item1, :bluetop_item2, :bluetop_item3, :bluetop_item4, :bluetop_item5, 
                    :bluetop_rune0, :bluetop_rune1, :bluetop_rune2, :bluetop_rune3, :bluetop_rune4, :bluetop_rune5, 
                    :redtop_id, :redtop_champ, :redtop_kills, :redtop_deaths, :redtop_assists, :redtop_item0, :redtop_item1, :redtop_item2, :redtop_item3, :redtop_item4, :redtop_item5, 
                    :redtop_rune0, :redtop_rune1, :redtop_rune2, :redtop_rune3, :redtop_rune4, :redtop_rune5, 
                    :bluejg_id, :bluejg_champ, :bluejg_kills, :bluejg_deaths, :bluejg_assists, :bluejg_item0, :bluejg_item1, :bluejg_item2, :bluejg_item3, :bluejg_item4, :bluejg_item5, 
                    :bluejg_rune0, :bluejg_rune1, :bluejg_rune2, :bluejg_rune3, :bluejg_rune4, :bluejg_rune5, 
                    :redjg_id, :redjg_champ, :redjg_kills, :redjg_deaths, :redjg_assists, :redjg_item0, :redjg_item1, :redjg_item2, :redjg_item3, :redjg_item4, :redjg_item5, 
                    :redjg_rune0, :redjg_rune1, :redjg_rune2, :redjg_rune3, :redjg_rune4, :redjg_rune5, 
                    :bluemid_id, :bluemid_champ, :bluemid_kills, :bluemid_deaths, :bluemid_assists, :bluemid_item0, :bluemid_item1, :bluemid_item2, :bluemid_item3, :bluemid_item4, :bluemid_item5, 
                    :bluemid_rune0, :bluemid_rune1, :bluemid_rune2, :bluemid_rune3, :bluemid_rune4, :bluemid_rune5, 
                    :redmid_id, :redmid_champ, :redmid_kills, :redmid_deaths, :redmid_assists, :redmid_item0, :redmid_item1, :redmid_item2, :redmid_item3, :redmid_item4, :redmid_item5, 
                    :redmid_rune0, :redmid_rune1, :redmid_rune2, :redmid_rune3, :redmid_rune4, :redmid_rune5, 
                    :bluebot_id, :bluebot_champ, :bluebot_kills, :bluebot_deaths, :bluebot_assists, :bluebot_item0, :bluebot_item1, :bluebot_item2, :bluebot_item3, :bluebot_item4, :bluebot_item5, 
                    :bluebot_rune0, :bluebot_rune1, :bluebot_rune2, :bluebot_rune3, :bluebot_rune4, :bluebot_rune5, 
                    :redbot_id, :redbot_champ, :redbot_kills, :redbot_deaths, :redbot_assists, :redbot_item0, :redbot_item1, :redbot_item2, :redbot_item3, :redbot_item4, :redbot_item5, 
                    :redbot_rune0, :redbot_rune1, :redbot_rune2, :redbot_rune3, :redbot_rune4, :redbot_rune5, 
                    :bluesup_id, :bluesup_champ, :bluesup_kills, :bluesup_deaths, :bluesup_assists, :bluesup_item0, :bluesup_item1, :bluesup_item2, :bluesup_item3, :bluesup_item4, :bluesup_item5, 
                    :bluesup_rune0, :bluesup_rune1, :bluesup_rune2, :bluesup_rune3, :bluesup_rune4, :bluesup_rune5, 
                    :redsup_id, :redsup_champ, :redsup_kills, :redsup_deaths, :redsup_assists, :redsup_item0, :redsup_item1, :redsup_item2, :redsup_item3, :redsup_item4, :redsup_item5, 
                    :redsup_rune0, :redsup_rune1, :redsup_rune2, :redsup_rune3, :redsup_rune4, :redsup_rune5
                )
                """), {
                    "match_code": match_code, "game_stamp": game_stamp, "game_duration": game_duration, "result": outcome, "patch": patch,
                    "bluetop_id": bluetop_id, "bluetop_champ": bluetop_champ, "bluetop_kills": bluetop_kills, "bluetop_deaths": bluetop_deaths, "bluetop_assists": bluetop_assists, "bluetop_item0": bluetop_item0, "bluetop_item1": bluetop_item1, 
                    "bluetop_item2": bluetop_item2, "bluetop_item3": bluetop_item3, "bluetop_item4": bluetop_item4, "bluetop_item5": bluetop_item5, 
                    "bluetop_rune0": bluetop_rune0, "bluetop_rune1": bluetop_rune1, "bluetop_rune2": bluetop_rune2, "bluetop_rune3": bluetop_rune3, 
                    "bluetop_rune4": bluetop_rune4, "bluetop_rune5": bluetop_rune5, 
                    "redtop_id": redtop_id, "redtop_champ": redtop_champ, "redtop_kills": redtop_kills, "redtop_deaths": redtop_deaths, "redtop_assists": redtop_assists, "redtop_item0": redtop_item0, "redtop_item1": redtop_item1, 
                    "redtop_item2": redtop_item2, "redtop_item3": redtop_item3, "redtop_item4": redtop_item4, "redtop_item5": redtop_item5, 
                    "redtop_rune0": redtop_rune0, "redtop_rune1": redtop_rune1, "redtop_rune2": redtop_rune2, "redtop_rune3": redtop_rune3, 
                    "redtop_rune4": redtop_rune4, "redtop_rune5": redtop_rune5, 
                    "bluejg_id": bluejg_id, "bluejg_champ": bluejg_champ, "bluejg_kills": bluejg_kills, "bluejg_deaths": bluejg_deaths, "bluejg_assists": bluejg_assists, "bluejg_item0": bluejg_item0, "bluejg_item1": bluejg_item1, 
                    "bluejg_item2": bluejg_item2, "bluejg_item3": bluejg_item3, "bluejg_item4": bluejg_item4, "bluejg_item5": bluejg_item5, 
                    "bluejg_rune0": bluejg_rune0, "bluejg_rune1": bluejg_rune1, "bluejg_rune2": bluejg_rune2, "bluejg_rune3": bluejg_rune3, 
                    "bluejg_rune4": bluejg_rune4, "bluejg_rune5": bluejg_rune5, 
                    "redjg_id": redjg_id, "redjg_champ": redjg_champ, "redjg_kills": redjg_kills, "redjg_deaths": redjg_deaths, "redjg_assists": redjg_assists, "redjg_item0": redjg_item0, "redjg_item1": redjg_item1, 
                    "redjg_item2": redjg_item2, "redjg_item3": redjg_item3, "redjg_item4": redjg_item4, "redjg_item5": redjg_item5, 
                    "redjg_rune0": redjg_rune0, "redjg_rune1": redjg_rune1, "redjg_rune2": redjg_rune2, "redjg_rune3": redjg_rune3, 
                    "redjg_rune4": redjg_rune4, "redjg_rune5": redjg_rune5, 
                    "bluemid_id": bluemid_id, "bluemid_champ": bluemid_champ, "bluemid_kills": bluemid_kills, "bluemid_deaths": bluemid_deaths, "bluemid_assists": bluemid_assists, "bluemid_item0": bluemid_item0, "bluemid_item1": bluemid_item1, 
                    "bluemid_item2": bluemid_item2, "bluemid_item3": bluemid_item3, "bluemid_item4": bluemid_item4, "bluemid_item5": bluemid_item5, 
                    "bluemid_rune0": bluemid_rune0, "bluemid_rune1": bluemid_rune1, "bluemid_rune2": bluemid_rune2, "bluemid_rune3": bluemid_rune3, 
                    "bluemid_rune4": bluemid_rune4, "bluemid_rune5": bluemid_rune5, 
                    "redmid_id": redmid_id, "redmid_champ": redmid_champ, "redmid_kills": redmid_kills, "redmid_deaths": redmid_deaths, "redmid_assists": redmid_assists, "redmid_item0": redmid_item0, "redmid_item1": redmid_item1, 
                    "redmid_item2": redmid_item2, "redmid_item3": redmid_item3, "redmid_item4": redmid_item4, "redmid_item5": redmid_item5, 
                    "redmid_rune0": redmid_rune0, "redmid_rune1": redmid_rune1, "redmid_rune2": redmid_rune2, "redmid_rune3": redmid_rune3, 
                    "redmid_rune4": redmid_rune4, "redmid_rune5": redmid_rune5, 
                    "bluebot_id": bluebot_id, "bluebot_champ": bluebot_champ, "bluebot_kills": bluebot_kills, "bluebot_deaths": bluebot_deaths, "bluebot_assists": bluebot_assists, "bluebot_item0": bluebot_item0, "bluebot_item1": bluebot_item1, 
                    "bluebot_item2": bluebot_item2, "bluebot_item3": bluebot_item3, "bluebot_item4": bluebot_item4, "bluebot_item5": bluebot_item5, 
                    "bluebot_rune0": bluebot_rune0, "bluebot_rune1": bluebot_rune1, "bluebot_rune2": bluebot_rune2, "bluebot_rune3": bluebot_rune3, 
                    "bluebot_rune4": bluebot_rune4, "bluebot_rune5": bluebot_rune5, 
                    "redbot_id": redbot_id, "redbot_champ": redbot_champ, "redbot_kills": redbot_kills, "redbot_deaths": redbot_deaths, "redbot_assists": redbot_assists, "redbot_item0": redbot_item0, "redbot_item1": redbot_item1, 
                    "redbot_item2": redbot_item2, "redbot_item3": redbot_item3, "redbot_item4": redbot_item4, "redbot_item5": redbot_item5, 
                    "redbot_rune0": redbot_rune0, "redbot_rune1": redbot_rune1, "redbot_rune2": redbot_rune2, "redbot_rune3": redbot_rune3, 
                    "redbot_rune4": redbot_rune4, "redbot_rune5": redbot_rune5, 
                    "bluesup_id": bluesup_id, "bluesup_champ": bluesup_champ, "bluesup_kills": bluesup_kills, "bluesup_deaths": bluesup_deaths, "bluesup_assists": bluesup_assists, "bluesup_item0": bluesup_item0, "bluesup_item1": bluesup_item1, 
                    "bluesup_item2": bluesup_item2, "bluesup_item3": bluesup_item3, "bluesup_item4": bluesup_item4, "bluesup_item5": bluesup_item5, 
                    "bluesup_rune0": bluesup_rune0, "bluesup_rune1": bluesup_rune1, "bluesup_rune2": bluesup_rune2, "bluesup_rune3": bluesup_rune3, 
                    "bluesup_rune4": bluesup_rune4, "bluesup_rune5": bluesup_rune5, 
                    "redsup_id": redsup_id, "redsup_champ": redsup_champ, "redsup_kills": redsup_kills, "redsup_deaths": redsup_deaths, "redsup_assists": redsup_assists, "redsup_item0": redsup_item0, "redsup_item1": redsup_item1, 
                    "redsup_item2": redsup_item2, "redsup_item3": redsup_item3, "redsup_item4": redsup_item4, "redsup_item5": redsup_item5, 
                    "redsup_rune0": redsup_rune0, "redsup_rune1": redsup_rune1, "redsup_rune2": redsup_rune2, "redsup_rune3": redsup_rune3, 
                    "redsup_rune4": redsup_rune4, "redsup_rune5": redsup_rune5 
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
                print("Fetching matches since last update")
                for match in all_matches:
                    print("Fetching match data") 
                    details = fetch_match_data(match, api_key, region)
                    if details is not None:
                        (time_stamp, game_duration, result,
                        bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, bluetop_item0, bluetop_item1, bluetop_item2, bluetop_item3, bluetop_item4, bluetop_item5, bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5,
                        
                        # Blue JG
                        bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, bluejg_item0, bluejg_item1, bluejg_item2, bluejg_item3, bluejg_item4, bluejg_item5, bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5,
                        
                        # Blue Mid
                        bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, bluemid_item0, bluemid_item1, bluemid_item2, bluemid_item3, bluemid_item4, bluemid_item5, bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5,
                        
                        # Blue Bot
                        bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, bluebot_item0, bluebot_item1, bluebot_item2, bluebot_item3, bluebot_item4, bluebot_item5, bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5,
                        
                        # Blue Sup
                        bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, bluesup_item0, bluesup_item1, bluesup_item2, bluesup_item3, bluesup_item4, bluesup_item5, bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5,
                        
                        # Red Top
                        redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, redtop_item0, redtop_item1, redtop_item2, redtop_item3, redtop_item4, redtop_item5, redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5,
                        
                        # Red JG
                        redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, redjg_item0, redjg_item1, redjg_item2, redjg_item3, redjg_item4, redjg_item5, redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5,
                        
                        # Red Mid
                        redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, redmid_item0, redmid_item1, redmid_item2, redmid_item3, redmid_item4, redmid_item5, redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5,
                        
                        # Red Bot
                        redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, redbot_item0, redbot_item1, redbot_item2, redbot_item3, redbot_item4, redbot_item5, redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5,
                        
                        # Red Sup
                        redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, redsup_item0, redsup_item1, redsup_item2, redsup_item3, redsup_item4, redsup_item5, redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5
                        ) = details
                        time.sleep(0.8)
                        print("Inserting the game")
                        insert_game(match, time_stamp, engine, game_duration, result, patch,
                            bluetop_id, bluetop_champ, bluetop_kills, bluetop_deaths, bluetop_assists, item_map[bluetop_item0], item_map[bluetop_item1], item_map[bluetop_item2], item_map[bluetop_item3], item_map[bluetop_item4], item_map[bluetop_item5], rune_map[bluetop_rune0], rune_map[bluetop_rune1], rune_map[bluetop_rune2], rune_map[bluetop_rune3], rune_map[bluetop_rune4], rune_map[bluetop_rune5],
                            
                            # Blue JG
                            bluejg_id, bluejg_champ, bluejg_kills, bluejg_deaths, bluejg_assists, item_map[bluejg_item0], item_map[bluejg_item1], item_map[bluejg_item2], item_map[bluejg_item3], item_map[bluejg_item4], item_map[bluejg_item5], rune_map[bluejg_rune0], rune_map[bluejg_rune1], rune_map[bluejg_rune2], rune_map[bluejg_rune3], rune_map[bluejg_rune4], rune_map[bluejg_rune5],
                            
                            # Blue Mid
                            bluemid_id, bluemid_champ, bluemid_kills, bluemid_deaths, bluemid_assists, item_map[bluemid_item0], item_map[bluemid_item1], item_map[bluemid_item2], item_map[bluemid_item3], item_map[bluemid_item4], item_map[bluemid_item5], rune_map[bluemid_rune0], rune_map[bluemid_rune1], rune_map[bluemid_rune2], rune_map[bluemid_rune3], rune_map[bluemid_rune4], rune_map[bluemid_rune5],
                            
                            # Blue Botfetch_item(
                            bluebot_id, bluebot_champ, bluebot_kills, bluebot_deaths, bluebot_assists, item_map[bluebot_item0], item_map[bluebot_item1], item_map[bluebot_item2], item_map[bluebot_item3], item_map[bluebot_item4], item_map[bluebot_item5], rune_map[bluebot_rune0], rune_map[bluebot_rune1], rune_map[bluebot_rune2], rune_map[bluebot_rune3], rune_map[bluebot_rune4], rune_map[bluebot_rune5],
                            
                            # Blue Sup
                            bluesup_id, bluesup_champ, bluesup_kills, bluesup_deaths, bluesup_assists, item_map[bluesup_item0], item_map[bluesup_item1], item_map[bluesup_item2], item_map[bluesup_item3], item_map[bluesup_item4], item_map[bluesup_item5], rune_map[bluesup_rune0], rune_map[bluesup_rune1], rune_map[bluesup_rune2], rune_map[bluesup_rune3], rune_map[bluesup_rune4], rune_map[bluesup_rune5],
                            
                            # Red Top
                            redtop_id, redtop_champ, redtop_kills, redtop_deaths, redtop_assists, item_map[redtop_item0], item_map[redtop_item1], item_map[redtop_item2], item_map[redtop_item3], item_map[redtop_item4], item_map[redtop_item5], rune_map[redtop_rune0], rune_map[redtop_rune1], rune_map[redtop_rune2], rune_map[redtop_rune3], rune_map[redtop_rune4], rune_map[redtop_rune5],
                            
                            # Red JG
                            redjg_id, redjg_champ, redjg_kills, redjg_deaths, redjg_assists, item_map[redjg_item0], item_map[redjg_item1], item_map[redjg_item2], item_map[redjg_item3], item_map[redjg_item4], item_map[redjg_item5], rune_map[redjg_rune0], rune_map[redjg_rune1], rune_map[redjg_rune2], rune_map[redjg_rune3], rune_map[redjg_rune4], rune_map[redjg_rune5],
                            # Red Mid
                            redmid_id, redmid_champ, redmid_kills, redmid_deaths, redmid_assists, item_map[redmid_item0], item_map[redmid_item1], item_map[redmid_item2], item_map[redmid_item3], item_map[redmid_item4], item_map[redmid_item5], rune_map[redmid_rune0], rune_map[redmid_rune1], rune_map[redmid_rune2], rune_map[redmid_rune3], rune_map[redmid_rune4], rune_map[redmid_rune5],
                            
                            # Red Bot
                            redbot_id, redbot_champ, redbot_kills, redbot_deaths, redbot_assists, item_map[redbot_item0], item_map[redbot_item1], item_map[redbot_item2], item_map[redbot_item3], item_map[redbot_item4], item_map[redbot_item5], rune_map[redbot_rune0], rune_map[redbot_rune1], rune_map[redbot_rune2], rune_map[redbot_rune3], rune_map[redbot_rune4], rune_map[redbot_rune5],
                            
                            # Red Sup
                            redsup_id, redsup_champ, redsup_kills, redsup_deaths, redsup_assists, item_map[redsup_item0], item_map[redsup_item1], item_map[redsup_item2], item_map[redsup_item3], item_map[redsup_item4], item_map[redsup_item5], rune_map[redsup_rune0], rune_map[redsup_rune1], rune_map[redsup_rune2], rune_map[redsup_rune3], rune_map[redsup_rune4], rune_map[redsup_rune5]
                        )
                    print("Inserted game into database")
                    insert_player(engine, player[1], player[2], player[3], player[4], player[5], player[6], player[7], player[8], player[9], datetime.now())
                    print("updated timestamp")


            