from sqlalchemy import create_engine, text
from collections import defaultdict
import rune
import numpy as np
def model_item_data(engine, item_map):
    sql = """
        -- Top lane matchups
        SELECT
        bluetop_champ AS champion,
        bluetop_item0 AS item0_used,
        bluetop_item1 AS item1_used,
        bluetop_item2 AS item2_used,
        bluetop_item3 AS item3_used,
        bluetop_item4 AS item4_used,
        bluetop_item5 AS item5_used,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        'top' AS lane
        FROM highelo_matches
        UNION ALL
        SELECT
        redtop_champ AS champion,
        redtop_item0 AS item0_used,
        redtop_item1 AS item1_used,
        redtop_item2 AS item2_used,
        redtop_item3 AS item3_used,
        redtop_item4 AS item4_used,
        redtop_item5 AS item5_used,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        'top' AS lane
        FROM highelo_matches
        UNION ALL

        -- Jungle matchups
        SELECT
        bluejg_champ AS champion,
        bluejg_item0 AS item0_used,
        bluejg_item1 AS item1_used,
        bluejg_item2 AS item2_used,
        bluejg_item3 AS item3_used,
        bluejg_item4 AS item4_used,
        bluejg_item5 AS item5_used,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        'jg' AS lane
        FROM highelo_matches
        UNION ALL
        SELECT
        redjg_champ AS champion,
        redjg_item0 AS item0_used,
        redjg_item1 AS item1_used,
        redjg_item2 AS item2_used,
        redjg_item3 AS item3_used,
        redjg_item4 AS item4_used,
        redjg_item5 AS item5_used,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        'jg' AS lane
        FROM highelo_matches
        UNION ALL

        -- Mid lane matchups
        SELECT
        bluemid_champ AS champion,
        bluemid_item0 AS item0_used,
        bluemid_item1 AS item1_used,
        bluemid_item2 AS item2_used,
        bluemid_item3 AS item3_used,
        bluemid_item4 AS item4_used,
        bluemid_item5 AS item5_used,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        'mid' AS lane
        FROM highelo_matches
        UNION ALL
        SELECT
        redmid_champ AS champion,
        redmid_item0 AS item0_used,
        redmid_item1 AS item1_used,
        redmid_item2 AS item2_used,
        redmid_item3 AS item3_used,
        redmid_item4 AS item4_used,
        redmid_item5 AS item5_used,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        'mid' AS lane
        FROM highelo_matches
        UNION ALL

        -- Bot lane matchups (ADC)
        SELECT
        bluebot_champ AS champion,
        bluebot_item0 AS item0_used,
        bluebot_item1 AS item1_used,
        bluebot_item2 AS item2_used,
        bluebot_item3 AS item3_used,
        bluebot_item4 AS item4_used,
        bluebot_item5 AS item5_used,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        'bot' AS lane
        FROM highelo_matches
        UNION ALL
        SELECT
        redbot_champ AS champion,
        redbot_item0 AS item0_used,
        redbot_item1 AS item1_used,
        redbot_item2 AS item2_used,
        redbot_item3 AS item3_used,
        redbot_item4 AS item4_used,
        redbot_item5 AS item5_used,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        'bot' AS lane
        FROM highelo_matches
        UNION ALL

        -- Support matchups
        SELECT
        bluesup_champ AS champion,
        bluesup_item0 AS item0_used,
        bluesup_item1 AS item1_used,
        bluesup_item2 AS item2_used,
        bluesup_item3 AS item3_used,
        bluesup_item4 AS item4_used,
        bluesup_item5 AS item5_used,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        'sup' AS lane
        FROM highelo_matches
        UNION ALL
        SELECT
        redsup_champ AS champion,
        redsup_item0 AS item0_used,
        redsup_item1 AS item1_used,
        redsup_item2 AS item2_used,
        redsup_item3 AS item3_used,
        redsup_item4 AS item4_used,
        redsup_item5 AS item5_used,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        'sup' AS lane
        FROM highelo_matches;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), {
        })
        results = result.fetchall()
        champ_map = rune.champ_mapping()
        actual_data = []
        for row in results:
            champion_name = row[0]
            item0 = row[1]
            item1 = row[2]
            item2 = row[3]
            item3 = row[4]
            item4 = row[5]
            item5 = row[6]
            opponent_top = row[7]
            opponent_jg = row[8]
            opponent_mid = row[9]
            opponent_bot = row[10]
            opponent_sup = row[11]
            lane = row[12]
            champion_type = champ_map[champion_name]["type"]
            champion_damage = champ_map[champion_name]["damage"]
            champion_role = champ_map[champion_name]["role"]
            
            opponent_top_type = champ_map[opponent_top]["type"]
            opponent_top_damage = champ_map[opponent_top]["damage"]
            opponent_top_role = champ_map[opponent_top]["role"]

            opponent_jg_type = champ_map[opponent_jg]["type"]
            opponent_jg_damage = champ_map[opponent_jg]["damage"]
            opponent_jg_role = champ_map[opponent_jg]["role"]
            
            opponent_mid_type = champ_map[opponent_mid]["type"]
            opponent_mid_damage = champ_map[opponent_mid]["damage"]
            opponent_mid_role = champ_map[opponent_mid]["role"]

            opponent_bot_type = champ_map[opponent_bot]["type"]
            opponent_bot_damage = champ_map[opponent_bot]["damage"]
            opponent_bot_role = champ_map[opponent_bot]["role"]

            opponent_sup_type = champ_map[opponent_sup]["type"]
            opponent_sup_damage = champ_map[opponent_sup]["damage"]
            opponent_sup_role = champ_map[opponent_sup]["role"]

            actual_data.append({
                'champion': champion_name,
                'champion_type': champion_type,
                'champion_damage': champion_damage,
                'champion_role': champion_role,
                'item0': item0 if item0 is not None and item_map[item0]['status'] == 'completed' and item_map[item0]['gold'] > 900 else np.nan,
                'item1': item1 if item1 is not None and item_map[item1]['status'] == 'completed' and item_map[item1]['gold'] > 900 else np.nan,
                'item2': item2 if item2 is not None and item_map[item2]['status'] == 'completed' and item_map[item2]['gold'] > 900 else np.nan,
                'item3': item3 if item3 is not None and item_map[item3]['status'] == 'completed' and item_map[item3]['gold'] > 900 else np.nan,
                'item4': item4 if item4 is not None and item_map[item4]['status'] == 'completed' and item_map[item4]['gold'] > 900 else np.nan,
                'item5': item5 if item5 is not None and item_map[item5]['status'] == 'completed' and item_map[item5]['gold'] > 900 else np.nan,
                'lane': lane,
                'opponent_top': opponent_top,
                'opponent_top_type': opponent_top_type,
                'opponent_top_damage': opponent_top_damage,
                'opponent_top_role': opponent_top_role,
                'opponent_jg': opponent_jg,
                'opponent_jg_type': opponent_jg_type,
                'opponent_jg_damage': opponent_jg_damage,
                'opponent_jg_role': opponent_jg_role,
                'opponent_mid': opponent_mid,
                'opponent_mid_type': opponent_mid_type,
                'opponent_mid_damage': opponent_mid_damage,
                'opponent_mid_role': opponent_mid_role,
                'opponent_bot': opponent_bot,
                'opponent_bot_type': opponent_bot_type,
                'opponent_bot_damage': opponent_bot_damage,
                'opponent_bot_role': opponent_bot_role,
                'opponent_sup': opponent_sup,
                'opponent_sup_type': opponent_sup_type,
                'opponent_sup_damage': opponent_sup_damage,
                'opponent_sup_role': opponent_sup_role,
            })
        return actual_data