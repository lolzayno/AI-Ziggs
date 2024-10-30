from flask import Flask, jsonify

import pickle
import keras
import numpy as np
import pandas as pd
from tensorflow import keras

app = Flask(__name__)

@app.route("/")
def hello():
    return "hello"

@app.route("/runes/<string:champion>/<string:lane>/<string:opponent>")
def get_rune(champion, lane, opponent):
    champion_map = champ_mapping()
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
    
    model_rune, le, feature_columns = load_rune_model()
    predicted_rune_page = predict_rune_page(model_rune, le, new_data, feature_columns)
    predicted_rune_page = predicted_rune_page[0].split('-')

    return jsonify(predicted_rune_page)

# @app.route("/items/<string:champion>/<string:lane>/<string:opponent_top>/<string:opponent_jg>/<string:opponent_mid>/<string:opponent_bot>/<string:opponent_sup>")
# def get_item(champion, lane, opponent_top, opponent_jg, opponent_mid, opponent_bot, opponent_sup):
#     champion_map = champ_mapping()
#     new_data_item = [{
#         'champion': champion,
#         'champion_type': champion_map[champion]['type'],
#         'champion_damage': champion_map[champion]['damage'],
#         'champion_role': champion_map[champion]['role'],
#         'lane': lane,
#         'opponent_top': opponent_top,
#         'opponent_top_type': champion_map[opponent_top]['type'],
#         'opponent_top_damage': champion_map[opponent_top]['damage'],
#         'opponent_top_role': champion_map[opponent_top]['role'],
#         'opponent_jg': opponent_jg,
#         'opponent_jg_type': champion_map[opponent_jg]['type'],
#         'opponent_jg_damage': champion_map[opponent_jg]['damage'],
#         'opponent_jg_role': champion_map[opponent_jg]['role'],
#         'opponent_mid': opponent_mid,
#         'opponent_mid_type': champion_map[opponent_mid]['type'],
#         'opponent_mid_damage': champion_map[opponent_mid]['damage'],
#         'opponent_mid_role': champion_map[opponent_mid]['role'],
#         'opponent_bot': opponent_bot,
#         'opponent_bot_type': champion_map[opponent_bot]['type'],
#         'opponent_bot_damage': champion_map[opponent_bot]['damage'],
#         'opponent_bot_role': champion_map[opponent_bot]['role'],
#         'opponent_sup': opponent_sup,
#         'opponent_sup_type': champion_map[opponent_sup]['type'],
#         'opponent_sup_damage': champion_map[opponent_sup]['damage'],
#         'opponent_sup_role': champion_map[opponent_sup]['role']
#     }]
#     models, x_columns, item_classes = load_item_model()
#     item_prediction = predict_items(models, new_data_item, x_columns, item_classes)
#     items_list = [item_prediction[items][0] for items in item_prediction]
    
#     return jsonify(items_list)
def champ_mapping():
    champion_attributes = {
    "Aatrox": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Ahri": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Akali": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Akshan": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Alistar": {"type": "melee", "damage": "AD", "role": "support"},
    "Amumu": {"type": "melee", "damage": "AP", "role": "tank"},
    "Anivia": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Annie": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Aphelios": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Ashe": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "AurelionSol": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Aurora": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Azir": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Bard": {"type": "ranged", "damage": "AP", "role": "support"},
    "Belveth": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Blitzcrank": {"type": "melee", "damage": "AD", "role": "support"},
    "Brand": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Braum": {"type": "melee", "damage": "AD", "role": "support"},
    "Briar": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Caitlyn": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Camille": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Cassiopeia": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Chogath": {"type": "melee", "damage": "AP", "role": "tank"},
    "Corki": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Darius": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Diana": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Draven": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "DrMundo": {"type": "melee", "damage": "AD/AP", "role": "tank"},
    "Ekko": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Elise": {"type": "ranged/melee", "damage": "AP", "role": "assassin"},
    "Evelynn": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Ezreal": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "FiddleSticks": {"type": "ranged", "damage": "AP", "role": "assassin"},
    "Fiora": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Fizz": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Galio": {"type": "melee", "damage": "AP", "role": "mage"},
    "Gangplank": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Garen": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Gnar": {"type": "ranged/melee", "damage": "AD", "role": "bruiser"},
    "Gragas": {"type": "melee", "damage": "AP", "role": "tank/mage"},
    "Graves": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Gwen": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Hecarim": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Heimerdinger": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Hwei": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Illaoi": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Irelia": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Ivern": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Janna": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "JarvanIV": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Jax": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Jayce": {"type": "ranged/melee", "damage": "AD", "role": "bruiser"},
    "Jhin": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Jinx": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Kaisa": {"type": "ranged", "damage": "AD/AP", "role": "marksman"},
    "Kalista": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Karma": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Karthus": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Kassadin": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Katarina": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Kayle": {"type": "ranged/melee", "damage": "AD/AP", "role": "marksman"},
    "Kayn": {"type": "melee", "damage": "AD", "role": "assassin/bruiser"},
    "Kennen": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Khazix": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Kindred": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Kled": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "KogMaw": {"type": "ranged", "damage": "AD/AP", "role": "marksman"},
    "KSante": {"type": "melee", "damage": "AD", "role": "tank"},
    "Leblanc": {"type": "ranged", "damage": "AP", "role": "assassin"},
    "LeeSin": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Leona": {"type": "melee", "damage": "AD", "role": "support"},
    "Lillia": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Lissandra": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Lucian": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Lulu": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Lux": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Malphite": {"type": "melee", "damage": "AP", "role": "tank"},
    "Malzahar": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Maokai": {"type": "melee", "damage": "AP", "role": "tank"},
    "MasterYi": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Milio": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "MissFortune": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Mordekaiser": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Morgana": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Naafiri": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Nami": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Nasus": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Nautilus": {"type": "melee", "damage": "AP", "role": "support"},
    "Neeko": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Nidalee": {"type": "ranged/melee", "damage": "AP", "role": "assassin"},
    "Nilah": {"type": "melee", "damage": "AD", "role": "marksman"},
    "Nocturne": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Nunu": {"type": "melee", "damage": "AP", "role": "tank"},
    "Olaf": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Orianna": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Ornn": {"type": "melee", "damage": "AD/AP", "role": "tank"},
    "Pantheon": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Poppy": {"type": "melee", "damage": "AD", "role": "tank"},
    "Pyke": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Qiyana": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Quinn": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Rakan": {"type": "melee", "damage": "AP", "role": "support"},
    "Rammus": {"type": "melee", "damage": "AD", "role": "tank"},
    "RekSai": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Rell": {"type": "melee", "damage": "AD", "role": "support"},
    "Renata": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Renekton": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Rengar": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Riven": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Rumble": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Ryze": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Samira": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Sejuani": {"type": "melee", "damage": "AP", "role": "tank"},
    "Senna": {"type": "ranged", "damage": "AD", "role": "marksman/enchanter"},
    "Seraphine": {"type": "ranged", "damage": "AP", "role": "mage/enhanter"},
    "Sett": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Shaco": {"type": "melee", "damage": "AD/AP", "role": "assassin"},
    "Shen": {"type": "melee", "damage": "AD", "role": "tank"},
    "Shyvana": {"type": "melee", "damage": "AD/AP", "role": "bruiser"},
    "Singed": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Sion": {"type": "melee", "damage": "AD", "role": "tank"},
    "Sivir": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Skarner": {"type": "melee", "damage": "AP", "role": "tank"},
    "Smolder": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Sona": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Soraka": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Swain": {"type": "ranged", "damage": "AP", "role": "bruiser"},
    "Sylas": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Syndra": {"type": "ranged", "damage": "AP", "role": "mage"},
    "TahmKench": {"type": "melee", "damage": "AD/AP", "role": "tank"},
    "Taliyah": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Talon": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Taric": {"type": "melee", "damage": "AP", "role": "support"},
    "Teemo": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Thresh": {"type": "melee", "damage": "AP", "role": "support"},
    "Tristana": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Trundle": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Tryndamere": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "TwistedFate": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Twitch": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Udyr": {"type": "melee", "damage": "AD/AP", "role": "bruiser"},
    "Urgot": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Varus": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Vayne": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Veigar": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Velkoz": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vex": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vi": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Viego": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Viktor": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vladimir": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Volibear": {"type": "melee", "damage": "AD/AP", "role": "bruiser"},
    "Warwick": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "MonkeyKing": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Xayah": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Xerath": {"type": "ranged", "damage": "AP", "role": "mage"},
    "XinZhao": {"type": "ranged", "damage": "AD", "role": "bruiser"},
    "Yasuo": {"type": "melee", "damage": "AD", "role": "marksman"},
    "Yone": {"type": "melee", "damage": "AD", "role": "marksman"},
    "Yorick": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Yuumi": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Zac": {"type": "melee", "damage": "AP", "role": "tank"},
    "Zed": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Zeri": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Ziggs": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Zilean": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Zoe": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Zyra": {"type": "ranged", "damage": "AP", "role": "mage"}
    }
    return champion_attributes
def load_rune_model():
    # Load the model
    model = keras.models.load_model('models/rune_model.keras')  # Load the model from the models folder

    # Load the label encoder
    with open('models/label_encoder.pkl', 'rb') as le_file:
        le = pickle.load(le_file)  # Load the label encoder

    # Load the feature columns
    with open('models/feature_columns.pkl', 'rb') as col_file:
        feature_columns = pickle.load(col_file)  # Load the feature columns

    return model, le, feature_columns  # Return the loaded model, label encoder, and feature columns


def predict_rune_page(model, le, new_data, x_columns):
    #Convert new_data to DataFrame
    df_new = pd.DataFrame([new_data])
    
    # One-hot encode categorical input features
    df_encoded = pd.get_dummies(df_new, columns=['champion', 'champion_type', 'champion_damage', 
                                                 'champion_role', 'lane', 'opponent_name', 
                                                 'opponent_type', 'opponent_damage', 
                                                 'opponent_role'])

    # Ensure the new data has the same columns as the training data
    missing_cols = set(x_columns) - set(df_encoded.columns)
    
    # Create a dictionary for missing columns filled with zeros
    missing_data = {col: [0] for col in missing_cols}  # Use list to match DataFrame structure

    # Concatenate missing columns to the existing DataFrame
    df_encoded = pd.concat([df_encoded, pd.DataFrame(missing_data)], axis=1)

    # Rearrange the columns to match the training input order
    df_encoded = df_encoded.reindex(columns=x_columns, fill_value=0)
    # Convert to integers and then to float
    df_encoded = df_encoded.astype(int)  # Convert boolean to int
    x_input = df_encoded.values.astype(np.float32)  # Ensure input is float32
    # Prepare the input for prediction
    x_input = df_encoded.values
    # Make prediction
    predicted_class_index = model.predict(x_input)
    predicted_class_index = np.argmax(predicted_class_index, axis=1)  # Get the class with the highest probability

    # Convert predicted class index back to rune page
    predicted_rune_page = le.inverse_transform(predicted_class_index)

    return predicted_rune_page

def get_predicted_rune_page(champion, lane, opponent):
    champion_map = champ_mapping()
    
    # Prepare new data dictionary for prediction
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

    # Load model and make prediction
    model_rune, le, feature_columns = load_rune_model()
    predicted_rune_page = predict_rune_page(model_rune, le, new_data, feature_columns)
    return predicted_rune_page[0].split('-')

if __name__ == "__main__":
    app.run(debug=True)
