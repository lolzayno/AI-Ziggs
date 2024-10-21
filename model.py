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
import tensorflow as tf
import keras
from keras import Sequential
import item
import backend
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras

def rune_model(data):
    df = pd.DataFrame(data)

    # One-hot encode categorical input features
    df_encoded = pd.get_dummies(df, columns=['champion', 'champion_type', 'champion_damage', 'champion_role', 
                                             'lane', 'opponent_name', 'opponent_type', 'opponent_damage', 
                                             'opponent_role'])

    # Prepare input features
    x_data = df_encoded.drop(columns=['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5'])

    # Create a single column for rune pages
    df['rune_page'] = df[['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5']].apply(lambda x: '-'.join(x), axis=1)
    
    # Encode the rune pages
    le = LabelEncoder()
    y_data = le.fit_transform(df['rune_page'])

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)

    # Build the neural network model
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(len(le.classes_), activation='softmax')  # Use softmax for multi-class
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

    # Evaluate the model
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_accuracy:.3f}")

    return model, le, x_data.columns  # Return x_data.columns for use in predictions


def predict_rune_page(model, le, new_data, x_columns):
    # Convert new_data to DataFrame
    df_new = pd.DataFrame([new_data])
    
    # One-hot encode categorical input features
    df_encoded = pd.get_dummies(df_new, columns=['champion', 'champion_type', 'champion_damage', 
                                                 'champion_role', 'lane', 'opponent_name', 
                                                 'opponent_type', 'opponent_damage', 
                                                 'opponent_role'])

    # Ensure the new data has the same columns as the training data
    for col in x_columns:  # Use the columns from the training set
        if col not in df_encoded.columns:
            df_encoded[col] = 0  # Fill missing columns with zeros

    # Rearrange the columns to match the training input order
    df_encoded = df_encoded.reindex(columns=x_columns, fill_value=0)

    # Prepare the input for prediction
    x_input = df_encoded.values

    # Make prediction
    predicted_class_index = model.predict(x_input)
    predicted_class_index = np.argmax(predicted_class_index, axis=1)  # Get the class with the highest probability

    # Convert predicted class index back to rune page
    predicted_rune_page = le.inverse_transform(predicted_class_index)

    return predicted_rune_page

def item_model(data, item_map):
    # Create DataFrame from input data
    df = pd.DataFrame(data)

    # One-hot encode categorical input features
    df_encoded = pd.get_dummies(df, columns=[
        'champion', 'champion_type', 'champion_damage', 
        'champion_role', 'lane', 
        'opponent_top', 'opponent_top_type', 'opponent_top_damage', 'opponent_top_role', 
        'opponent_jg', 'opponent_jg_type', 'opponent_jg_damage', 'opponent_jg_role', 
        'opponent_mid', 'opponent_mid_type', 'opponent_mid_damage', 'opponent_mid_role', 
        'opponent_bot', 'opponent_bot_type', 'opponent_bot_damage', 'opponent_bot_role', 
        'opponent_sup', 'opponent_sup_type', 'opponent_sup_damage', 'opponent_sup_role'
    ])

    # Drop item columns for features
    x_data = df_encoded.drop(columns=['item0', 'item1', 'item2', 'item3', 'item4', 'item5'])

    # Expand the data to make each item a separate row
    expanded_data = []
    for index, row in df.iterrows():
        for item in ['item0', 'item1', 'item2', 'item3', 'item4', 'item5']:
            current_item = row[item]
            # Check if the current item is not None and if it is completed
            if current_item is not None and current_item in item_map and item_map[current_item]['status'] == 'completed':
                expanded_data.append(row.drop([item]).tolist() + [current_item])
    
    # Check if expanded_data is empty
    if not expanded_data:
        raise ValueError("No completed items found for the provided data.")

    # Create new DataFrame from expanded data
    expanded_df = pd.DataFrame(expanded_data, columns=x_data.columns.tolist() + ['item'])
    # Drop items that are not completed or None
    expanded_df = expanded_df[expanded_df['item'].notnull()]
    # Split data into features and target
    x_data = expanded_df.drop(columns=['item'])
    y_data = expanded_df['item']
    y_data_encoded = pd.get_dummies(y_data)
    # Split into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data_encoded, test_size=0.2, random_state=42)

    # Create the model
    model = Sequential()
    model.add(keras.layers.Dense(128, activation='relu', input_shape=(x_train.shape[1],)))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(len(y_data.unique()), activation='softmax'))  # Unique classes for the output layer

    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(x_train, y_train, epochs=50, batch_size=10, validation_split=0.2)

    # Evaluate the model
    loss, accuracy = model.evaluate(x_test, y_test)
    print(f'Test Accuracy: {accuracy:.2f}')

    return model, x_data.columns

# Prediction function
def predict_items(model, new_data, item_map, x_data):
    new_df = pd.DataFrame([new_data])
    new_df_encoded = pd.get_dummies(new_df, columns=[...])  # One-hot encode like before

    # Ensure it has the same columns as the training data
    new_df_encoded = new_df_encoded.reindex(columns=x_data.columns, fill_value=0)

    predictions = model.predict(new_df_encoded)

    # Convert predictions to items
    predicted_items = []
    for i in range(predictions.shape[1]):
        predicted_item_index = np.argmax(predictions[:, i])
        predicted_item = item_map[predicted_item_index]['name']
        predicted_items.append(predicted_item)

    return predicted_items

if __name__ == '__main__':
    api_key = chatbot.get_json("API_KEY")
    engine = chatbot.establish_connection()
    patch = backend.fetch_patch()
    champion_map = backend.champ_map(patch)
    rune_map = backend.fetch_rune(patch)
    item_map = backend.fetch_item(patch)
    data_rune = rune.final_rune_data(engine)
    models_rune, le = rune_model(data_rune)
    model, le, x_columns = rune_model(data_rune)  # Get x_columns from the model training
    new_data = {
        'champion': 'Ziggs',
        'champion_type': 'Ranged',
        'champion_damage': 'AP',
        'champion_role': 'Mage',
        'lane': 'Mid',
        'opponent_name': 'Leblanc',
        'opponent_type': 'Ranged',
        'opponent_damage': 'AP',
        'opponent_role': 'Assassin',
    }

    predicted_rune_page = predict_rune_page(model, le, new_data, x_columns)
    print(f"Predicted Rune Page: {predicted_rune_page}")

    data_item = item.model_item_data(engine)
    models_item, x_data = item_model(data_item, item_map)
    new_data_item = {
        'champion': 'Ziggs',
        'champion_type': 'Ranged',
        'champion_damage': 'AP',
        'champion_role': 'Mage',
        'lane': 'Mid',
        'opponent_top': 'Camille',
        'opponent_top_type': 'Melee',
        'opponent_top_damage': 'AD',
        'opponent_top_role': 'Bruiser',
        'opponent_jg': 'Zac',
        'opponent_jg_type': 'Melee',
        'opponent_jg_damage': 'AP',
        'opponent_jg_role': 'Tank',
        'opponent_mid': 'Leblanc',
        'opponent_mid_type': 'Ranged',
        'opponent_mid_damage': 'AP',
        'opponent_mid_role': 'Assassin',
        'opponent_bot': 'Kaisa',
        'opponent_bot_type': 'Ranged',
        'opponent_bot_damage': 'AD/AP',
        'opponent_bot_role': 'Marksman',
        'opponent_sup': 'Rakan',
        'opponent_sup_type': 'Melee',
        'opponent_sup_damage': 'AP',
        'opponent_sup_role': 'Support'
    }
    item_prediction = predict_items(models_item, new_data_item, item_map, x_data)