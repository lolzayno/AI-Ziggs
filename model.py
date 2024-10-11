import sklearn
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import chatbot
import rune
import backend
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
import item
def rune_model(data):
    df = pd.DataFrame(data, columns=['champion', 'primary_rune', 'secondary_rune', 'third_rune', 'fourth_rune', 'fifth_rune', 'sixth_rune', 'opponent', 'lane'])

    # Features are 'champion', 'opponent', and 'lane' (already converted to IDs)
    x = df[['champion','opponent', 'lane']].astype(int)

    # Target is the runes for each slot
    y = df[['primary_rune', 'secondary_rune', 'third_rune', 'fourth_rune', 'fifth_rune', 'sixth_rune']].astype(str)

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Train a RandomForest for each rune slot
    models = {}
    rune_slots = ['primary_rune', 'secondary_rune', 'third_rune', 'fourth_rune', 'fifth_rune', 'sixth_rune']

    for rune_slot in rune_slots:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train[rune_slot])
        models[rune_slot] = model

    # Make predictions and calculate accuracy for each rune slot
    for rune_slot in rune_slots:
        predictions = models[rune_slot].predict(X_test)
        accuracy = accuracy_score(y_test[rune_slot], predictions)
        print(f"{rune_slot.capitalize()} Prediction Accuracy: {accuracy:.2f}")

    return models
def predict_runes(models, input_data):
    # Prepare the input data as a DataFrame
    input_df = pd.DataFrame([input_data], columns=['champion', 'opponent', 'lane'])
    
    # Make predictions for each rune slot
    predictions = {}
    for rune_slot in models.keys():
        predictions[rune_slot] = models[rune_slot].predict(input_df)[0]
    
    return predictions

def item_model(data):
    # Create a DataFrame with columns for the champion, opponents, lane, and items
    df = pd.DataFrame(data, columns=['champion', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'opponent1', 'opponent2', 'opponent3', 'opponent4', 'opponent5', 'lane'])

    # Input features: Champion, primary opponent, other opponents, and lane
    X = df[['champion', 'opponent1', 'opponent2', 'opponent3', 'opponent4', 'opponent5', 'lane']].astype(int)

    # Target labels: The 6 items
    y = df[['item1', 'item2', 'item3', 'item4', 'item5', 'item6']].astype(str)

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a RandomForest for each item slot
    models = {}
    item_slots = ['item1', 'item2', 'item3', 'item4', 'item5', 'item6']

    for item_slot in item_slots:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train[item_slot])
        models[item_slot] = model

    # Make predictions and calculate accuracy for each item slot
    for item_slot in item_slots:
        predictions = models[item_slot].predict(X_test)
        accuracy = accuracy_score(y_test[item_slot], predictions)
        print(f"{item_slot.capitalize()} Prediction Accuracy: {accuracy:.2f}")

    return models

def predict_items(models, input_data):
    # Prepare the input data as a DataFrame
    input_df = pd.DataFrame([input_data], columns=['champion', 'opponent1', 'opponent2', 'opponent3', 'opponent4', 'opponent5', 'lane'])
    
    # Make predictions for each rune slot
    predictions = {}
    for item_slot in models.keys():
        predictions[item_slot] = models[item_slot].predict(input_df)[0]
    
    return predictions

if __name__ == '__main__':
    api_key = chatbot.get_json("API_KEY")
    engine = chatbot.establish_connection()
    patch = backend.fetch_patch()
    champion_map = backend.champ_map(patch)
    rune_map = backend.fetch_rune(patch)
    item_map = backend.fetch_item(patch)
    data_rune = rune.model_rune_data(engine)
    models_rune = rune_model(data_rune)
    rune_dict = predict_runes(models_rune, [champion_map['Udyr'], champion_map['Darius'], 0])
    for runer in rune_dict:
        print(rune_map[int(rune_dict[runer])])

    data_item = item.model_item_data(engine)
    models_item = item_model(data_item)
    item_dict = predict_items(models_item, [champion_map['Udyr'], champion_map['Darius'], champion_map['Graves'], champion_map['Zed'], champion_map['Samira'], champion_map['Nautilus'], 0])
    for itemer in item_dict:
        print(item_map[int(item_dict[itemer])])
    