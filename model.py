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

def rune_model(data):
    # Step 1: Convert data to DataFrame
    df = pd.DataFrame(data)

    # Step 2: Split the data into features (x_data) and labels (y_data)
    x_data = df.drop(columns=['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5'])
    y_data = df[['rune0', 'rune1', 'rune2', 'rune3', 'rune4', 'rune5']]

    # Step 3: Split the data into training and test sets
    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)

    # Step 4: Initialize a list of LabelEncoders for each rune column
    label_encoders = [LabelEncoder() for _ in range(6)]

    # Step 5: Fit and transform y_train and y_test for each rune
    y_train_list = [label_encoders[i].fit_transform(y_train[f'rune{i}']) for i in range(6)]
    y_test_list = [label_encoders[i].transform(y_test[f'rune{i}']) for i in range(6)]

    # Step 6: Define the input layer for the model
    input_layer = keras.Input(shape=(x_train.shape[1],))

    # Shared dense layers
    shared_layer = keras.layers.Dense(64, activation='relu')(input_layer)
    shared_layer = keras.layers.Dense(32, activation='relu')(shared_layer)

    # Step 7: Create separate output layers for each rune prediction
    outputs = []
    for i in range(6):
        output = keras.layers.Dense(len(label_encoders[i].classes_), activation='softmax')(shared_layer)
        outputs.append(output)

    # Step 8: Create the model with multiple outputs
    model = keras.Model(inputs=input_layer, outputs=outputs)

    # Step 9: Compile the model
    model.compile(optimizer='adam', 
                  loss=['sparse_categorical_crossentropy'] * 6, 
                  metrics=['accuracy'] * 6)

    # Step 10: Train the model
    model.fit(x_train, y_train_list, epochs=50, batch_size=10, validation_split=0.2)

    # Step 11: Evaluate the model on the test set
    accuracy = model.evaluate(x_test, y_test_list)
    print(f'Test Accuracy: {accuracy}')

    return model




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
    model.add(Dense(64, activation='relu', input_shape=(x_train.shape[1],)))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(len(y_data.unique()), activation='softmax'))  # Unique classes for the output layer

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
    print(champion_map)
    rune_map = backend.fetch_rune(patch)
    item_map = backend.fetch_item(patch)
    data_rune = rune.final_rune_data(engine)
    models_rune = rune_model(data_rune)

    