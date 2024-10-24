from fastapi import FastAPI
import rune
import model

app = FastAPI()

@app.get("/")
def hello():
    return "hello"

@app.get("/runes/{champion}/{lane}/{opponent}")
def get_rune(champion: str, lane: str, opponent: str) -> list[str]:
    champion_map = rune.champ_mapping()
    new_data = {
        'champion': champion,
        'champion_type': champion_map[champion]['type'],
        'champion_damage': champion_map[champion]['damage'],
        'champion_role': champion_map[champion]['role'],
        'lane': lane,
        'opponent_name': opponent,
        'opponent_type': champion_map[opponent]['type'],
        'opponent_damage': champion_map[opponent]['damage'],
        'opponent_role': champion_map[opponent]['role']
    }
    
    model_rune, le, feature_columns = model.load_rune_model()
    predicted_rune_page = model.predict_rune_page(model_rune, le, new_data, feature_columns)
    predicted_rune_page = predicted_rune_page[0].split('-')

    return predicted_rune_page

@app.get("/items/{champion}/{lane}/{opponent_top}/{opponent_jg}/{opponent_mid}/{opponent_bot}/{opponent_sup}")
def get_item(champion: str, lane: str, opponent_top: str, opponent_jg: str, opponent_mid: str, opponent_bot: str, opponent_sup: str):
    champion_map = rune.champ_mapping()
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
    models, x_columns, item_classes = model.load_item_model()
    item_prediction = model.predict_items(models, new_data_item, x_columns, item_classes)
    items_list = []
    for items in item_prediction:
        items_list.append(item_prediction[items][0])
    
    return items_list