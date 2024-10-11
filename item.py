from sqlalchemy import create_engine, text
from collections import defaultdict
def model_item_data(engine):
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
        0 AS lane
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
        0 AS lane
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
        1 AS lane
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
        1 AS lane
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
        2 AS lane
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
        2 AS lane
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
        3 AS lane
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
        3 AS lane
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
        4 AS lane
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
        4 AS lane
        FROM highelo_matches;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), {
        })
        results = result.fetchall()
        return results