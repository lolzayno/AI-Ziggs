import os
import json
import requests
import pytz
import datetime
from sqlalchemy import create_engine, text

def establish_connection():
    engine = create_engine(f'mysql+mysqlconnector://{get_json("user")}:{get_json("host_pw")}@{get_json("host_host")}/{get_json("database")}')
    try:
        with engine.connect() as connection:
            print("Connection to the database was successful!")
    except Exception as e:
        print(f"Error: {e}")

    return engine

def get_json(subject):
    script_dir = os.path.dirname(__file__)

    config_path = os.path.join(script_dir,'config.json')

    with open(config_path, 'r') as file:
        config = json.load(file)

    return config.get(subject)

def fetch_challenger(region, api_key):
    challenger_link = f'https://{region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(challenger_link)
    return response.json()
def fetch_grandmaster(region, api_key):
    grandmaster_link = f'https://{region}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(grandmaster_link)
    return response.json()
def fetch_master(region, api_key):
    master_link = f'https://{region}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}'
    response = requests.get(master_link)
    return response.json()

def fetch_matches(region, fetched_id, api_key):
    if region in ['BR1', 'LA1', 'LA2', 'NA1', 'OC1']:
        region = 'americas'
    elif region in ['JP1', 'KR']:
        region = 'asia'
    elif region in ['EUW1', 'EUN1', 'RU', 'TR1', 'ME1']:
        region = 'europe'
    else:
        region = 'sea'

    time_zone = pytz.timezone('America/Los_Angeles')
    season_start = int(datetime(2024, 5, 15, 12, 0, 0, tzinfo=time_zone).timestamp())
    type_match = 'ranked'
    starting_index = 0
    matches_requested = 100
    all_matches = []
    while True:
        matches_api_url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{fetched_id}/ids?startTime={season_start}&type={type_match}&start={starting_index}&count={matches_requested}&api_key={api_key}'
        response = requests.get(matches_api_url)
        if response.status_code != 200:
            print(f"Error fetching matches: {response.status_code}")
            break
        bundled_matches = response.json()
        if not bundled_matches:
            break
            
        all_matches.extend(bundled_matches)
        

        starting_index += matches_requested

    return all_matches

def get_puuid(summoner_id, api_key, region):
    get_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}'
    response = requests.get(get_url)
    return response.json()['puuid']

def get_ign(puuid, api_key, region):
    if region in ['BR1', 'LA1', 'LA2', 'NA1', 'OC1']:
        region = 'americas'
    elif region in ['JP1', 'KR', 'PH2', 'SG2', 'TH2', 'TW2', 'VN2']:
        region = 'asia'
    elif region in ['EUW1', 'EUN1', 'RU', 'TR1', 'ME1']:
        region = 'europe'
    get_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}"
    response = requests.get(get_url)
    data = response.json()
    return data['gameName'], data['tagLine']

def update_players(player_list, engine, region, api_key, rank):
    for player in player_list['entries']:
        puuid = get_puuid(player['summonerId'], api_key, region)
        ign, tag = get_ign(puuid, api_key, region)
        insert_player(engine, player['summonerId'], ign, tag, region, rank, player['leaguePoints'], player['wins'], player['losses'], datetime.now())

def insert_player(engine, summoner_id, summoner_name, summoner_tag, summoner_region, summoner_rank, summoner_lp, summoner_wins, summoner_losses, last_updated):
    with engine.connect() as connection:
        connection.execute(text("INSERT INTO highelo_player(summoner_id, summoner_name, summoner_tag, summoner_region, summoner_rank, summoner_lp, summoner_wins, summoner_losses, last_updated) VALUES (:summoner_id, :summoner_name, :summoner_tag, :summoner_region, :summoner_rank, :summoner_lp, :summoner_wins, :summoner_losses, :last_updated)"), {"summoner_id": summoner_id, "summoner_name": summoner_name, "summoner_tag": summoner_tag, "summoner_region": summoner_region, "summoner_rank": summoner_rank, "summoner_lp": summoner_lp, "summoner_wins": summoner_wins, "summoner_losses": summoner_losses, "last_updated": last_updated})
        result = connection.execute(text("""
            SELECT * FROM highelo_player
            WHERE summoner_id = :summoner_id
            """), {"summoner_id": summoner_id})
        row = result.fetchone()

    return
if __name__ == '__main__':
    api_key = get_json("API_KEY") #Fetches api key
    challenger = fetch_challenger('na1', api_key) #gets challenger players
    grandmaster = fetch_grandmaster('na1', api_key) #gets grandmaster players
    master = fetch_master('na1', api_key) #get master players
    engine = establish_connection() #establishes connection to database
    update_players(grandmaster, engine) #Updates players in database
    region_list = ['BR1', 'EUW1', 'EUN1', 'JP1', 'KR', 'LA1', 'LA2', 'ME1', 'NA1', 'OC1', 'PH2', 'RU', 'SG2', 'TH2', 'TR1', 'TW2', 'VN2']