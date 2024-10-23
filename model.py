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
    #Put data into correct form to be processed
    df = pd.DataFrame(data)

    #One-hot encode categorical input features
    df_encoded = pd.get_dummies(df, columns=['champion', 'champion_type', 'champion_damage', 'champion_role', 
                                             'lane', 'opponent_name', 'opponent_type', 'opponent_damage', 
                                             'opponent_role'])

    #Prepare input features by dropping rune columns (rune0 to rune5)
    x_data = df_encoded.drop(columns=['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5', 'rune6', 'rune7', 'rune8'])
    # Create a single column for rune pages
    df['rune_page'] = df[['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5','rune6', 'rune7', 'rune8']].apply(lambda x: '-'.join(x), axis=1)

    #List of columns to exclude (rune0 to rune8)
    rune_columns = ['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5', 'rune6', 'rune7', 'rune8']

    #Convert all columns except 'rune0' to 'rune8' to integers
    x_data = df_encoded.drop(columns=rune_columns)  # Select non-rune columns
    x_data = x_data.astype(int)  # Convert to integer

    #Encode the rune pages into integer labels
    le = LabelEncoder()
    y_data = le.fit_transform(df['rune_page'])
    #Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)

    # Build the neural network model with explicit Input layer
    model = keras.Sequential([
        keras.layers.Input(shape=(X_train.shape[1],)),  #Use Input layer for defining the shape
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(len(le.classes_), activation='softmax')  #Use softmax for multi-class classification
    ])

    #Compile the model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    #Train the model
    model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))

    #Evaluate the model
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_accuracy:.3f}")

    return model, le, x_data.columns  # Return x_data.columns for use in predictions

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

def item_model(data):

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

    # Drop item columns for features (X data)
    x_data = df_encoded.drop(columns=['item0', 'item1', 'item2', 'item3', 'item4', 'item5'])

    # Initialize dictionary to hold individual models for each item
    models = {}
    item_classes = {}  # To store the unique item names for each item column

    # Loop through each item column (item0, item1, ..., item5)
    for item_col in ['item0', 'item1', 'item2', 'item3','item4', 'item5']:
        # Filter out rows where the current item is None
        df_filtered = df[df[item_col].notna()]
        # One-hot encode the filtered item column
        y_data = pd.get_dummies(df_filtered[item_col])

        # Store the unique item names for mapping later
        item_classes[item_col] = y_data.columns.tolist()

        #Filter corresponding x_data (matching rows of the filtered df)
        x_data_filtered = x_data.loc[df_filtered.index]

        # Split into training and testing sets
        x_train, x_test, y_train, y_test = train_test_split(x_data_filtered, y_data, test_size=0.2, random_state=42)

        # Build a model for this item slot
        model = keras.Sequential([
            keras.layers.Input(shape=(x_train.shape[1],)),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(y_train.shape[1], activation='softmax')  # Use softmax for multi-class classification
        ])

        # Compile the model
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        model.fit(x_train, y_train, epochs=50, batch_size=10, validation_split=0.2)

        # Evaluate the model
        loss, accuracy = model.evaluate(x_test, y_test)
        print(f'Test Accuracy for {item_col}: {accuracy:.2f}')
        
        # Store the trained model
        models[item_col] = model

    return models, x_data.columns, item_classes

def predict_items(models, new_data, column_list, item_classes):
    # Convert new data to DataFrame
    new_df = pd.DataFrame(new_data)

    # One-hot encode the input features (similar to training)
    new_df_encoded = pd.get_dummies(new_df, columns=[
        'champion', 'champion_type', 'champion_damage', 
        'champion_role', 'lane', 
        'opponent_top', 'opponent_top_type', 'opponent_top_damage', 'opponent_top_role', 
        'opponent_jg', 'opponent_jg_type', 'opponent_jg_damage', 'opponent_jg_role', 
        'opponent_mid', 'opponent_mid_type', 'opponent_mid_damage', 'opponent_mid_role', 
        'opponent_bot', 'opponent_bot_type', 'opponent_bot_damage', 'opponent_bot_role', 
        'opponent_sup', 'opponent_sup_type', 'opponent_sup_damage', 'opponent_sup_role'
    ])

    # Ensure the new_df_encoded has the same columns as the original training data
    missing_cols = set(column_list) - set(new_df_encoded.columns)

    # Create a DataFrame for missing columns filled with zeros
    if missing_cols:
        missing_data = pd.DataFrame(0, index=np.arange(len(new_df_encoded)), columns=list(missing_cols))  # Convert set to list
        # Concatenate missing columns to the existing DataFrame
        new_df_encoded = pd.concat([new_df_encoded, missing_data], axis=1)

    # Rearrange the columns to match the training input order
    df_encoded = new_df_encoded.reindex(columns=column_list, fill_value=0)

    # Convert to integers and then to float
    df_encoded = df_encoded.astype(int)  # Convert boolean to int
    df_encoded = df_encoded.values.astype(np.float32)  # Ensure input is float32

    # Initialize dictionary to store predicted items
    predictions = {}

    # Loop through each item column and predict
    for item_col in ['item0', 'item1', 'item2', 'item3','item4', 'item5']:
        # Use the corresponding model to predict the item for this slot
        prediction_prob = models[item_col].predict(df_encoded)

        # Get the predicted item (highest probability)
        predicted_item = prediction_prob.argmax(axis=1)  # Get the class with the highest probability
        # Map indices back to actual item names
        predicted_items = [item_classes[item_col][index] for index in predicted_item]
        
        predictions[item_col] = predicted_items

    return predictions



if __name__ == '__main__':
    api_key = chatbot.get_json("API_KEY")
    engine = chatbot.establish_connection()
    patch = backend.fetch_patch()
    champion_map = backend.champ_map(patch)
    rune_map = backend.fetch_rune(patch)
    item_map = backend.fetch_item_model(patch)
    # data_rune = rune.final_rune_data(engine)
    # model, le, x_columns = rune_model(data_rune)  # Get x_columns from the model training
    # new_data = {
    #     'champion': 'Ziggs',
    #     'champion_type': 'ranged',
    #     'champion_damage': 'AP',
    #     'champion_role': 'mage',
    #     'lane': 'mid',
    #     'opponent_name': 'Syndra',
    #     'opponent_type': 'ranged',
    #     'opponent_damage': 'AP',
    #     'opponent_role': 'mage',
    # }

    # predicted_rune_page = predict_rune_page(model, le, new_data, x_columns)
    # print(f"Predicted Rune Page: {predicted_rune_page}")
    data_item = item.model_item_data(engine, item_map)
    models_item, x_data, item_class = item_model(data_item)
    new_data_item = [{
        'champion': 'Ziggs',
        'champion_type': 'ranged',
        'champion_damage': 'AP',
        'champion_role': 'mage',
        'lane': 'mid',
        'opponent_top': 'Camille',
        'opponent_top_type': 'melee',
        'opponent_top_damage': 'AD',
        'opponent_top_role': 'bruiser',
        'opponent_jg': 'Zac',
        'opponent_jg_type': 'melee',
        'opponent_jg_damage': 'AP',
        'opponent_jg_role': 'tank',
        'opponent_mid': 'Leblanc',
        'opponent_mid_type': 'ranged',
        'opponent_mid_damage': 'AP',
        'opponent_mid_role': 'assassin',
        'opponent_bot': 'Kaisa',
        'opponent_bot_type': 'ranged',
        'opponent_bot_damage': 'AD/AP',
        'opponent_bot_role': 'marksman',
        'opponent_sup': 'Rakan',
        'opponent_sup_type': 'melee',
        'opponent_sup_damage': 'AP',
        'opponent_sup_role': 'support'
    }]
    item_prediction = predict_items(models_item, new_data_item, x_data, item_class)
    print(item_prediction)