import os
import json
import openai
import time
from sqlalchemy import create_engine, text
from collections import defaultdict
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

def get_rune(engine, champ, lane):
    if lane == "top":
        sql_blue = """
        SELECT
            bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluetop_champ = :champ
                OR redtop_champ = :champ
            GROUP BY bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redtop_champ = :champ
            GROUP BY redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "jungle":
        sql_blue = """
        SELECT
            bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluejg_champ = :champ
            GROUP BY bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redjg_champ = :champ
            GROUP BY redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "mid":
        sql_blue = """
        SELECT
            bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluemid_champ = :champ
            GROUP BY bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redmid_champ = :champ
            GROUP BY redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "bot":
        sql_blue = """
        SELECT
            bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluebot_champ = :champ
            GROUP BY bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redbot_champ = :champ
            GROUP BY redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "support":
        sql_blue = """
        SELECT
            bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluesup_champ = :champ
            GROUP BY bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redsup_champ = :champ
            GROUP BY redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    with engine.connect() as connection:
        result_blue = connection.execute(text(sql_blue), {
            "champ": champ
        })
        result_red = connection.execute(text(sql_red), {
            "champ": champ
        })

         # Initialize a dictionary to accumulate rune counts
        rune_combinations = defaultdict(int)
        result_blue = result_blue.fetchall()
        result_red = result_red.fetchall()
        # Process blue side results
        for row in result_blue:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red:
            print(row)
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Convert the dictionary to a sorted list based on combo_count in descending order
        sorted_runes = sorted(rune_combinations.items(), key=lambda x: x[1], reverse=True)

        # Return the most common rune combination (top of the sorted list)
        if sorted_runes:
            top_rune_combo = sorted_runes[0]
            return top_rune_combo
        else:
            return None

def get_rune_specific(engine, champ, opponent, lane):
    if lane == "top":
        sql_blue = """
        SELECT
            bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluetop_champ = :champ
            AND redtop_champ = :opponent
            GROUP BY bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redtop_champ = :champ
            AND bluetop_champ = :opponent
            GROUP BY redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "jungle":
        sql_blue = """
        SELECT
            bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluejg_champ = :champ
            AND redjg_champ = :opponent
            GROUP BY bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redjg_champ = :champ
            AND bluejg_champ = :opponent
            GROUP BY redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "mid":
        sql_blue = """
        SELECT
            bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluemid_champ = :champ
            AND redmid_champ = :opponent
            GROUP BY bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redmid_champ = :champ
            AND bluemid_champ = :opponent
            GROUP BY redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "bot":
        sql_blue = """
        SELECT
            bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluebot_champ = :champ
            AND redbot_champ = :opponent
            GROUP BY bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redbot_champ = :champ
            AND bluebot_champ = :opponent
            GROUP BY redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    elif lane == "support":
        sql_blue = """
        SELECT
            bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE bluesup_champ = :champ
            AND redsup_champ = :opponent
            GROUP BY bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
        sql_red = """
        SELECT
            redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5,
            COUNT(*) AS combo_count
            FROM highelo_matches
            WHERE redsup_champ = :champ
            AND bluesup_champ = :opponent
            GROUP BY redsup_rune0, redsup_rune1, redsup_rune2, redsup_rune3, redsup_rune4, redsup_rune5
            ORDER BY combo_count DESC
            LIMIT 3;
        """
    with engine.connect() as connection:
        result_blue = connection.execute(text(sql_blue), {
            "champ": champ,
            "opponent": opponent
        })
        result_red = connection.execute(text(sql_red), {
            "champ": champ,
            "opponent": opponent
        })

         # Initialize a dictionary to accumulate rune counts
        rune_combinations = defaultdict(int)
        result_blue = result_blue.fetchall()
        result_red = result_red.fetchall()
        # Process blue side results
        for row in result_blue:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Convert the dictionary to a sorted list based on combo_count in descending order
        sorted_runes = sorted(rune_combinations.items(), key=lambda x: x[1], reverse=True)

        # Return the most common rune combination (top of the sorted list)
        if sorted_runes:
            top_rune_combo = sorted_runes[0]
            return top_rune_combo
        else:
            return None

if __name__ == '__main__':
    engine = establish_connection()
    # openai.api_key = get_json("openai_key")
    # memory_messages = []
    # while True:
    #     user_input = input("You: ")  # Get user input from the console
    #     response = get_chatbot_response(user_input, memory_messages)  # Get the chatbot response
    #     print(f"Chatbot: {response}")  # Print the chatbot's response
