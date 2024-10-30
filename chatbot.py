import os
import json
import openai
import time
from sqlalchemy import create_engine, text
import rune
import requests
import backend
import model
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
    champion_map = rune.champ_mapping()
    openai.api_key = get_json("openai_key")
    memory_messages = []
    rune_select = None
    print("Welcome to the League of Legends Rune Advisor! Ask about the best rune set.")
    while True:
        user_input = input("You: ")  # Get user input from the console
        try:
            if rune_select == 1:
                champion, opponent = user_input.split(" against ")
                champion = champion.capitalize()
                opponent = opponent.capitalize()
                new_data = {
                    'champion': champion,
                    'champion_type': champion_map[champion]['type'],
                    'champion_damage': champion_map[champion]['damage'],
                    'champion_role': champion_map[champion]['role'],
                    'lane': 'mid',
                    'opponent_name': opponent,
                    'opponent_type': champion_map[opponent]['type'],
                    'opponent_damage': champion_map[opponent]['damage'],
                    'opponent_role': champion_map[opponent]['role']
                }
                print(new_data)
                model_rune, le, feature_columns = model.load_rune_model()
                predicted_rune_page = model.predict_rune_page(model_rune, le, new_data, feature_columns)
                predicted_rune_page = predicted_rune_page[0].split('-')
                lane = 'mid'
                user_input = f"Please explain to this user who just requested a rune set for {champion} laning against {opponent} in the {lane} lane using this list of runes {predicted_rune_page}"
                response = get_chatbot_response(user_input, memory_messages)  # Get the chatbot response
                print(f"Chatbot: {response}")  # Print the chatbot's response
            else:
                champion, opponent = user_input.split(" against ")
                champion = champion.capitalize()
                opponent = opponent.split(',')
                opponent_top = opponent[0]
                opponent_jg = opponent[1]
                opponent_mid = opponent[2]
                opponent_bot = opponent[3]
                opponent_sup = opponent[4]
                new_data_item = [{
                    'champion': champion,
                    'champion_type': champion_map[champion]['type'],
                    'champion_damage': champion_map[champion]['damage'],
                    'champion_role': champion_map[champion]['role'],
                    'lane': 'mid',
                    'opponent_top': opponent_top,
                    'opponent_top_type': champion_map[opponent_top]['type'],
                    'opponent_top_damage': champion_map[opponent_top]['damage'],
                    'opponent_top_role': champion_map[opponent_top]['role'],
                    'opponent_jg': opponent_jg,
                    'opponent_jg_type': champion_map[opponent_jg]['type'],
                    'opponent_jg_damage': champion_map[opponent_jg]['damage'],
                    'opponent_jg_role': champion_map[opponent_jg]['role'],
                    'opponent_mid': opponent_mid,
                    'opponent_mid_type': champion_map[opponent_mid]['type'],
                    'opponent_mid_damage': champion_map[opponent_mid]['damage'],
                    'opponent_mid_role': champion_map[opponent_mid]['role'],
                    'opponent_bot': opponent_bot,
                    'opponent_bot_type': champion_map[opponent_bot]['type'],
                    'opponent_bot_damage': champion_map[opponent_bot]['damage'],
                    'opponent_bot_role': champion_map[opponent_bot]['role'],
                    'opponent_sup': opponent_sup,
                    'opponent_sup_type': champion_map[opponent_sup]['type'],
                    'opponent_sup_damage': champion_map[opponent_sup]['damage'],
                    'opponent_sup_role': champion_map[opponent_sup]['role']
                }]
                lane = 'mid'
                models, x_columns, item_classes = model.load_item_model()
                item_prediction = model.predict_items(models, new_data_item, x_columns, item_classes)
                items_list = []
                for items in item_prediction:
                    items_list.append(item_prediction[items][0])
                user_input = f"Please explain to this user who just requested a item set for {champion} in the {lane} lane,  going against {opponent_top} in top lane, {opponent_jg} in the jungle, {opponent_mid} in the mid lane, {opponent_bot} in the bot lane, and {opponent_sup} as the support using this list of items {items_list}. If there are repeated items, please substitute it would an item you think would be a better fit."
                response = get_chatbot_response(user_input, memory_messages)  # Get the chatbot response
                print(f"Chatbot: {response}")
        except ValueError:
            response_message = "Please provide input in the format: 'What is the best rune set for [champion] against [opponent]?'"
