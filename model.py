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
def rune_model(data):
    #Step 1: Convert data to DataFrame
    df = pd.DataFrame(data)

    #Step 2: Split the data into features (x_data) and labels (y_data)
    x_data = df.drop(columns=['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5'])
    y_data = df[['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5']]
    #Do i have to encode this or whatever to make the data better? Is there a way to give weights to each column?

    # Step 3: Split the data into training and test sets
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)

    #Step 4: Initialize a list of LabelEncoders for each rune column: WHY??
    label_encoders = [LabelEncoder() for _ in range(6)]

    #Step 5: Fit and transform y_train and y_test for each rune: WHAT DOES THIS DO?
    y_train_list = [label_encoders[i].fit_transform(y_train[f'rune{i}']) for i in range(6)]
    y_test_list = [label_encoders[i].transform(y_test[f'rune{i}']) for i in range(6)]

    # tep 6: Define the input layer for the model: WHAT DOES THIS DO
    input_layer = keras.Input(shape=(x_train.shape[1],))

    #Shared dense layers: WHAT DOES THIS DO??
    shared_layer = keras.layers.Dense(64, activation='relu')(input_layer)
    shared_layer = keras.layers.Dense(32, activation='relu')(shared_layer)

    #Step 7: Create separate output layers for each rune prediction: WHAT DOES THIS DO
    outputs = []
    for i in range(6):
        output = keras.layers.Dense(len(label_encoders[i].classes_), activation='softmax')(shared_layer)
        outputs.append(output)

    #Step 8: Create the model with multiple outputs: WHAT DOES THIS DO
    model = keras.Model(inputs=input_layer, outputs=outputs)

    #Step 9: Compile the model: WHAT DOES THIS DO?
    model.compile(optimizer='adam', 
                  loss=['sparse_categorical_crossentropy'] * 6, 
                  metrics=['accuracy'] * 6)

    #Step 10: Train the model: VALIDATION SPLIT??
    model.fit(x_train, y_train_list, epochs=50, batch_size=10, validation_split=0.2)

    # Step 11: Evaluate the model on the test set
    accuracy = model.evaluate(x_test, y_test_list)
    print(f'Test Accuracy: {accuracy}')

    return model, label_encoders

def predict_runes(model, new_data, label_encoders):
    # Convert the input to a DataFrame to match the format used during training
    x_new = pd.DataFrame(new_data)
    
    # Make predictions (the result will be a list of predictions, one for each rune)
    predictions = model.predict(x_new)
    
    # For each rune, pick the class with the highest probability
    predicted_runes = []
    for i, prediction in enumerate(predictions):
        # Get the index of the class with the highest probability
        predicted_class = prediction.argmax(axis=1)
        # Decode the index back to the original rune using the label encoder
        decoded_runes = label_encoders[i].inverse_transform(predicted_class)
        predicted_runes.append(decoded_runes)
    
    # Combine the predicted runes for each rune position
    # This will be a list of predictions for each row in `new_data`
    predicted_runes_combined = np.column_stack(predicted_runes).tolist()
    
    return predicted_runes_combined

def item_model(data, item_map):
    # Create DataFrame from input data
    df = pd.DataFrame(data)

    # Drop item columns for features
    x_data = df.drop(columns=['item0', 'item1', 'item2', 'item3', 'item4', 'item5'])
    
    # Select item columns for target
    y_data = df[['item0', 'item1', 'item2', 'item3', 'item4', 'item5']]
    # Expand the data to make each item a separate row
    expanded_data = []
    for index, row in df.iterrows():
        for item in ['item0', 'item1', 'item2', 'item3', 'item4', 'item5']:
            if item_map[row[item]]['status'] == 'completed':
                expanded_data.append(row.drop([item]).tolist() + [row[item]])
    
    # Create new DataFrame from expanded data
    expanded_df = pd.DataFrame(expanded_data, columns=x_data.columns.tolist() + ['item'])

    # Split data into features and target
    x_data = expanded_df.drop(columns=['item'])
    y_data = expanded_df['item']

    # Split into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)

    # Create the model
    model = Sequential()
    model.add(keras.layers.Dense(64, activation='relu', input_shape=(x_train.shape[1],)))
    model.add(keras.layers.Dense(32, activation='relu'))
    model.add(keras.layers.Dense(len(y_data.unique()), activation='softmax'))  # Unique classes for the output layer

    # Compile the model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(x_train, y_train, epochs=50, batch_size=10, validation_split=0.2)

    # Evaluate the model
    loss, accuracy = model.evaluate(x_test, y_test)
    print(f'Test Accuracy: {accuracy:.2f}')

    return model
if __name__ == '__main__':
    api_key = chatbot.get_json("API_KEY")
    engine = chatbot.establish_connection()
    patch = backend.fetch_patch()
    champion_map = backend.champ_map(patch)
    rune_map = backend.fetch_rune(patch)
    item_map = backend.fetch_item(patch)
    data_rune = rune.final_rune_data(engine)
    # models_rune, label_encoders = rune_model(data_rune)
    # new_data = [{'champion': 115,
    #             'champion_type': 1,
    #             'champion_damage': 1,
    #             'champion_role': 4,
    #             'lane': 2,
    #             'opponent_name': 238,
    #             'opponent_type': 0,
    #             'opponent_damage': 0,
    #             'opponent_role': 2}]
    # rune_prediction = predict_runes(models_rune, new_data, label_encoders)
    # print(rune_prediction)
    # for runer in rune_prediction[0]:
    #     print(rune_map[runer])

    