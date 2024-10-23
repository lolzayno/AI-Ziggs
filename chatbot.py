import os
import json
import openai
import time
from sqlalchemy import create_engine, text
import rune
import requests
import backend
def establish_connection():
    engine = create_engine(f'mysql+mysqlconnector://{get_json("user")}:{get_json("host_pw")}@{get_json("host_host")}/{get_json("database")}')
    try:
        with engine.connect() as connection:
            print("Connection to the database was successful!")
    except Exception as e:
        print(f"Error: {e}")

    return engine
# Fetches stuff from the JSON file
def get_json(subject):
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, 'config.json')

    with open(config_path, 'r') as file:
        config = json.load(file)

    return config.get(subject)

def get_chatbot_response(user_input, messages):
    messages.append({"role": "user", "content": user_input})
    while True:
        try:
            # Corrected line to use the appropriate method for accessing ChatCompletion
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            assistant_message = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})
            if len(messages) > 10:
                messages.pop(0)
            return assistant_message
        
        # Handle general API errors
        except Exception as e:
            print(f"Error: {e}")
            if 'Rate limit' in str(e):
                print("Rate limit exceeded. Retrying in 10 seconds...")
                time.sleep(10)  # Wait for 10 seconds before retrying
            else:
                return "Sorry, I couldn't get a response."

#fetches all matches of a specific champ
def get_match(engine, champ):
    sql = """
    SELECT * FROM highelo_matches
    WHERE bluetop_champ = :champ
    OR bluejg_champ = :champ
    OR bluemid_champ = :champ
    OR bluebot_champ = :champ
    OR bluesup_champ = :champ
    OR redtop_champ = :champ
    OR redjg_champ = :champ
    OR redmid_champ = :champ
    OR redbot_champ = :champ
    OR redsup_champ = :champ
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), {
            "champ": champ
        })
        rows = result.fetchall()
        processed_rows = [list(row[3:]) for row in rows]
        return processed_rows

def fetch_puuid(region, ign, tag, api_key):
    if region in ['BR1', 'LA1', 'LA2', 'NA1', 'OC1']:
        region = 'americas'
    elif region in ['JP1', 'KR', 'PH2', 'SG2', 'TH2', 'TW2', 'VN2']:
        region = 'asia'
    elif region in ['EUW1', 'EUN1', 'RU', 'TR1', 'ME1']:
        region = 'europe'
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{ign}/{tag}?api_key={api_key}'
    response = requests.get(url)
    print("Fetching puuid")
    print(response.status_code)
    return response.json()['puuid']

def spectate_game(region, puuid, api_key):
    url = f'https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={api_key}'
    response = requests.get(url)
    print("Fetching puuid")
    print(response.status_code)
    data = response.json()
    participants = data['participants']
    opponents = {}
    for player in participants:
        if player['puuid'] == puuid:
            champion = player['championId']
            team = player['teamId']
        elif player['teamId'] != team:
            opponents[player['championId']] = {
                    'spellId1': player['spell1Id'],
                    'spellId2': player['spell2Id'],
                    'runes': player['perks']  # Ensure you have runes data available
                }
    return opponents
if __name__ == '__main__':
    #item prediction output: {'item0': ["Mercury's Treads"], 'item1': ['Stormsurge'], 'item2': ['Horizon Focus'], 'item3': ["Rabadon's Deathcap"], 'item4': ['Void Staff'], 'item5': ["Banshee's Veil"]}
    #rune prediction output: Predicted Rune Page: ['Arcane Comet-Manaflow Band-Transcendence-Scorch-Presence of Mind-Cut Down-Adaptive Force-Adaptive Force-Health Growth']
    api_key = get_json("API_KEY")
    engine = establish_connection()
    openai.api_key = get_json("openai_key")
    memory_messages = []
    while True:
        user_input = input("You: ")  # Get user input from the console
        response = get_chatbot_response(user_input, memory_messages)  # Get the chatbot response
        print(f"Chatbot: {response}")  # Print the chatbot's response
