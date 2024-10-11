from sqlalchemy import create_engine, text
from collections import defaultdict

def model_item_data(engine):
    sql = """
        SELECT
        bluetop_champ AS champion,
        bluetop_kills AS kills,
        bluetop_deaths AS deaths,
        bluetop_assists AS assists,
        bluetop_kda AS kda, 
        bluetop_item0 AS item0_used,
        bluetop_item1 AS item1_used,
        bluetop_item2 AS item2_used,
        bluetop_item3 AS item3_used,
        bluetop_item4 AS item4_used,
        bluetop_item5 AS item5_used,
        bluetop_rune0 AS rune0_used,
        bluetop_rune1 AS rune1_used,
        bluetop_rune2 AS rune2_used,
        bluetop_rune3 AS rune3_used,
        bluetop_rune4 AS rune4_used,
        bluetop_rune5 AS rune5_used,
        bluetop_magicdmgdealt AS magicdmg_dealt,
        bluetop_physicaldmgdealt AS physicaldmg_dealt,
        bluetop_truedmgdealt AS truedmg_dealt,
        bluetop_ccdealt AS cc_dealt,
        bluetop_magicdmgreceive AS magicdmg_receive,
        bluetop_physicaldmgreceive AS physicaldmg_receive,
        bluetop_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 1  -- Blue team
            WHEN result = 'Red' THEN 0    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        0 AS lane
    FROM highelo_matches
    UNION ALL
    SELECT
        bluejg_champ AS champion,
        bluejg_kills AS kills,
        bluejg_deaths AS deaths,
        bluejg_assists AS assists,
        bluejg_kda AS kda, 
        bluejg_item0 AS item0_used,
        bluejg_item1 AS item1_used,
        bluejg_item2 AS item2_used,
        bluejg_item3 AS item3_used,
        bluejg_item4 AS item4_used,
        bluejg_item5 AS item5_used,
        bluejg_rune0 AS rune0_used,
        bluejg_rune1 AS rune1_used,
        bluejg_rune2 AS rune2_used,
        bluejg_rune3 AS rune3_used,
        bluejg_rune4 AS rune4_used,
        bluejg_rune5 AS rune5_used,
        bluejg_magicdmgdealt AS magicdmg_dealt,
        bluejg_physicaldmgdealt AS physicaldmg_dealt,
        bluejg_truedmgdealt AS truedmg_dealt,
        bluejg_ccdealt AS cc_dealt,
        bluejg_magicdmgreceive AS magicdmg_receive,
        bluejg_physicaldmgreceive AS physicaldmg_receive,
        bluejg_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 1  -- Blue team
            WHEN result = 'Red' THEN 0    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        1 AS lane,
    FROM highelo_matches

    UNION ALL

    SELECT
        bluemid_champ AS champion,
        bluemid_kills AS kills,
        bluemid_deaths AS deaths,
        bluemid_assists AS assists,
        bluemid_kda AS kda, 
        bluemid_item0 AS item0_used,
        bluemid_item1 AS item1_used,
        bluemid_item2 AS item2_used,
        bluemid_item3 AS item3_used,
        bluemid_item4 AS item4_used,
        bluemid_item5 AS item5_used,
        bluemid_rune0 AS rune0_used,
        bluemid_rune1 AS rune1_used,
        bluemid_rune2 AS rune2_used,
        bluemid_rune3 AS rune3_used,
        bluemid_rune4 AS rune4_used,
        bluemid_rune5 AS rune5_used,
        bluemid_magicdmgdealt AS magicdmg_dealt,
        bluemid_physicaldmgdealt AS physicaldmg_dealt,
        bluemid_truedmgdealt AS truedmg_dealt,
        bluemid_ccdealt AS cc_dealt,
        bluemid_magicdmgreceive AS magicdmg_receive,
        bluemid_physicaldmgreceive AS physicaldmg_receive,
        bluemid_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 1  -- Blue team
            WHEN result = 'Red' THEN 0    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        2 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluebot_champ AS champion,
        bluebot_kills AS kills,
        bluebot_deaths AS deaths,
        bluebot_assists AS assists,
        bluebot_kda AS kda, 
        bluebot_item0 AS item0_used,
        bluebot_item1 AS item1_used,
        bluebot_item2 AS item2_used,
        bluebot_item3 AS item3_used,
        bluebot_item4 AS item4_used,
        bluebot_item5 AS item5_used,
        bluebot_rune0 AS rune0_used,
        bluebot_rune1 AS rune1_used,
        bluebot_rune2 AS rune2_used,
        bluebot_rune3 AS rune3_used,
        bluebot_rune4 AS rune4_used,
        bluebot_rune5 AS rune5_used,
        bluebot_magicdmgdealt AS magicdmg_dealt,
        bluebot_physicaldmgdealt AS physicaldmg_dealt,
        bluebot_truedmgdealt AS truedmg_dealt,
        bluebot_ccdealt AS cc_dealt,
        bluebot_magicdmgreceive AS magicdmg_receive,
        bluebot_physicaldmgreceive AS physicaldmg_receive,
        bluebot_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 1  -- Blue team
            WHEN result = 'Red' THEN 0    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        3 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluesup_champ AS champion,
        bluesup_kills AS kills,
        bluesup_deaths AS deaths,
        bluesup_assists AS assists,
        bluesup_kda AS kda, 
        bluesup_item0 AS item0_used,
        bluesup_item1 AS item1_used,
        bluesup_item2 AS item2_used,
        bluesup_item3 AS item3_used,
        bluesup_item4 AS item4_used,
        bluesup_item5 AS item5_used,
        bluesup_rune0 AS rune0_used,
        bluesup_rune1 AS rune1_used,
        bluesup_rune2 AS rune2_used,
        bluesup_rune3 AS rune3_used,
        bluesup_rune4 AS rune4_used,
        bluesup_rune5 AS rune5_used,
        bluesup_magicdmgdealt AS magicdmg_dealt,
        bluesup_physicaldmgdealt AS physicaldmg_dealt,
        bluesup_truedmgdealt AS truedmg_dealt,
        bluesup_ccdealt AS cc_dealt,
        bluesup_magicdmgreceive AS magicdmg_receive,
        bluesup_physicaldmgreceive AS physicaldmg_receive,
        bluesup_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        redtop_champ AS opponent0,
        redjg_champ AS opponent1,
        redmid_champ AS opponent2,
        redbot_champ AS opponent3,
        redsup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 1  -- Blue team
            WHEN result = 'Red' THEN 0    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        4 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redtop_champ AS champion,
        redtop_kills AS kills,
        redtop_deaths AS deaths,
        redtop_assists AS assists,
        redtop_kda AS kda, 
        redtop_item0 AS item0_used,
        redtop_item1 AS item1_used,
        redtop_item2 AS item2_used,
        redtop_item3 AS item3_used,
        redtop_item4 AS item4_used,
        redtop_item5 AS item5_used,
        redtop_rune0 AS rune0_used,
        redtop_rune1 AS rune1_used,
        redtop_rune2 AS rune2_used,
        redtop_rune3 AS rune3_used,
        redtop_rune4 AS rune4_used,
        redtop_rune5 AS rune5_used,
        redtop_magicdmgdealt AS magicdmg_dealt,
        redtop_physicaldmgdealt AS physicaldmg_dealt,
        redtop_truedmgdealt AS truedmg_dealt,
        redtop_ccdealt AS cc_dealt,
        redtop_magicdmgreceive AS magicdmg_receive,
        redtop_physicaldmgreceive AS physicaldmg_receive,
        redtop_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 0  -- Blue team
            WHEN result = 'Red' THEN 1    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        0 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redjg_champ AS champion,
        redjg_kills AS kills,
        redjg_deaths AS deaths,
        redjg_assists AS assists,
        redjg_kda AS kda, 
        redjg_item0 AS item0_used,
        redjg_item1 AS item1_used,
        redjg_item2 AS item2_used,
        redjg_item3 AS item3_used,
        redjg_item4 AS item4_used,
        redjg_item5 AS item5_used,
        redjg_rune0 AS rune0_used,
        redjg_rune1 AS rune1_used,
        redjg_rune2 AS rune2_used,
        redjg_rune3 AS rune3_used,
        redjg_rune4 AS rune4_used,
        redjg_rune5 AS rune5_used,
        redjg_magicdmgdealt AS magicdmg_dealt,
        redjg_physicaldmgdealt AS physicaldmg_dealt,
        redjg_truedmgdealt AS truedmg_dealt,
        redjg_ccdealt AS cc_dealt,
        redjg_magicdmgreceive AS magicdmg_receive,
        redjg_physicaldmgreceive AS physicaldmg_receive,
        redjg_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 0  -- Blue team
            WHEN result = 'Red' THEN 1    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        1 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redmid_champ AS champion,
        redmid_kills AS kills,
        redmid_deaths AS deaths,
        redmid_assists AS assists,
        redmid_kda AS kda, 
        redmid_item0 AS item0_used,
        redmid_item1 AS item1_used,
        redmid_item2 AS item2_used,
        redmid_item3 AS item3_used,
        redmid_item4 AS item4_used,
        redmid_item5 AS item5_used,
        redmid_rune0 AS rune0_used,
        redmid_rune1 AS rune1_used,
        redmid_rune2 AS rune2_used,
        redmid_rune3 AS rune3_used,
        redmid_rune4 AS rune4_used,
        redmid_rune5 AS rune5_used,
        redmid_magicdmgdealt AS magicdmg_dealt,
        redmid_physicaldmgdealt AS physicaldmg_dealt,
        redmid_truedmgdealt AS truedmg_dealt,
        redmid_ccdealt AS cc_dealt,
        redmid_magicdmgreceive AS magicdmg_receive,
        redmid_physicaldmgreceive AS physicaldmg_receive,
        redmid_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 0  -- Blue team
            WHEN result = 'Red' THEN 1    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        2 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redbot_champ AS champion,
        redbot_kills AS kills,
        redbot_deaths AS deaths,
        redbot_assists AS assists,
        redbot_kda AS kda, 
        redbot_item0 AS item0_used,
        redbot_item1 AS item1_used,
        redbot_item2 AS item2_used,
        redbot_item3 AS item3_used,
        redbot_item4 AS item4_used,
        redbot_item5 AS item5_used,
        redbot_rune0 AS rune0_used,
        redbot_rune1 AS rune1_used,
        redbot_rune2 AS rune2_used,
        redbot_rune3 AS rune3_used,
        redbot_rune4 AS rune4_used,
        redbot_rune5 AS rune5_used,
        redbot_magicdmgdealt AS magicdmg_dealt,
        redbot_physicaldmgdealt AS physicaldmg_dealt,
        redbot_truedmgdealt AS truedmg_dealt,
        redbot_ccdealt AS cc_dealt,
        redbot_magicdmgreceive AS magicdmg_receive,
        redbot_physicaldmgreceive AS physicaldmg_receive,
        redbot_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 0  -- Blue team
            WHEN result = 'Red' THEN 1    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        3 AS lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redsup_champ AS champion,
        redsup_kills AS kills,
        redsup_deaths AS deaths,
        redsup_assists AS assists,
        redsup_kda AS kda, 
        redsup_item0 AS item0_used,
        redsup_item1 AS item1_used,
        redsup_item2 AS item2_used,
        redsup_item3 AS item3_used,
        redsup_item4 AS item4_used,
        redsup_item5 AS item5_used,
        redsup_rune0 AS rune0_used,
        redsup_rune1 AS rune1_used,
        redsup_rune2 AS rune2_used,
        redsup_rune3 AS rune3_used,
        redsup_rune4 AS rune4_used,
        redsup_rune5 AS rune5_used,
        redsup_magicdmgdealt AS magicdmg_dealt,
        redsup_physicaldmgdealt AS physicaldmg_dealt,
        redsup_truedmgdealt AS truedmg_dealt,
        redsup_ccdealt AS cc_dealt,
        redsup_magicdmgreceive AS magicdmg_receive,
        redsup_physicaldmgreceive AS physicaldmg_receive,
        redsup_truedmgreceive AS truedmg_receive,
        game_duration AS game_duration,
        bluetop_champ AS opponent0,
        bluejg_champ AS opponent1,
        bluemid_champ AS opponent2,
        bluebot_champ AS opponent3,
        bluesup_champ AS opponent4,
        CASE 
            WHEN result = 'Blue' THEN 0  -- Blue team
            WHEN result = 'Red' THEN 1    -- Red team
            ELSE NULL                     -- Handle unexpected values (optional)
        END AS result,
        4 AS lane
    FROM highelo_matches;

    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), {
        })
        results = result.fetchall()
        return results