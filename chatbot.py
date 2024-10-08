import os
import json
import openai
import time
from sqlalchemy import create_engine, text

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

if __name__ == '__main__':
    openai.api_key = get_json("openai_key")
    memory_messages = []
    while True:
        user_input = input("You: ")  # Get user input from the console
        response = get_chatbot_response(user_input, memory_messages)  # Get the chatbot response
        print(f"Chatbot: {response}")  # Print the chatbot's response
