from sqlalchemy import create_engine, text
from collections import defaultdict
#gets most popular rune by lane
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

#most popular rune by opponent and lane
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

#most popular rune in across all lanes
def get_rune_all(engine, champ):
    sql_blue_top= """
    SELECT
        bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE bluetop_champ = :champ
        GROUP BY bluetop_rune0, bluetop_rune1, bluetop_rune2, bluetop_rune3, bluetop_rune4, bluetop_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_red_top = """
    SELECT
        redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE redtop_champ = :champ
        GROUP BY redtop_rune0, redtop_rune1, redtop_rune2, redtop_rune3, redtop_rune4, redtop_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_blue_jg = """
    SELECT
        bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE bluejg_champ = :champ
        GROUP BY bluejg_rune0, bluejg_rune1, bluejg_rune2, bluejg_rune3, bluejg_rune4, bluejg_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_red_jg = """
    SELECT
        redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE redjg_champ = :champ
        GROUP BY redjg_rune0, redjg_rune1, redjg_rune2, redjg_rune3, redjg_rune4, redjg_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_blue_mid = """
    SELECT
        bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE bluemid_champ = :champ
        GROUP BY bluemid_rune0, bluemid_rune1, bluemid_rune2, bluemid_rune3, bluemid_rune4, bluemid_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_red_mid = """
    SELECT
        redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE redmid_champ = :champ
        GROUP BY redmid_rune0, redmid_rune1, redmid_rune2, redmid_rune3, redmid_rune4, redmid_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_blue_bot = """
    SELECT
        bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE bluebot_champ = :champ
        GROUP BY bluebot_rune0, bluebot_rune1, bluebot_rune2, bluebot_rune3, bluebot_rune4, bluebot_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_red_bot = """
    SELECT
        redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE redbot_champ = :champ
        GROUP BY redbot_rune0, redbot_rune1, redbot_rune2, redbot_rune3, redbot_rune4, redbot_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_blue_sup = """
    SELECT
        bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5,
        COUNT(*) AS combo_count
        FROM highelo_matches
        WHERE bluesup_champ = :champ
        GROUP BY bluesup_rune0, bluesup_rune1, bluesup_rune2, bluesup_rune3, bluesup_rune4, bluesup_rune5
        ORDER BY combo_count DESC
        LIMIT 3;
    """
    sql_red_sup = """
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
        result_blue_top = connection.execute(text(sql_blue_top), {
            "champ": champ
        })
        result_red_top = connection.execute(text(sql_red_top), {
            "champ": champ
        })
        result_blue_jg = connection.execute(text(sql_blue_jg), {
            "champ": champ
        })
        result_red_jg = connection.execute(text(sql_red_jg), {
            "champ": champ
        })
        result_blue_mid = connection.execute(text(sql_blue_mid), {
            "champ": champ
        })
        result_red_mid = connection.execute(text(sql_red_mid), {
            "champ": champ
        })
        result_blue_bot = connection.execute(text(sql_blue_bot), {
            "champ": champ
        })
        result_red_bot = connection.execute(text(sql_red_bot), {
            "champ": champ
        })
        result_blue_sup = connection.execute(text(sql_blue_sup), {
            "champ": champ
        })
        result_red_sup = connection.execute(text(sql_red_sup), {
            "champ": champ
        })

         # Initialize a dictionary to accumulate rune counts
        rune_combinations = defaultdict(int)
        result_blue_top = result_blue_top.fetchall()
        result_red_top = result_red_top.fetchall()
        result_blue_jg = result_blue_jg.fetchall()
        result_red_jg = result_red_jg.fetchall()
        result_blue_mid = result_blue_mid.fetchall()
        result_red_mid = result_red_mid.fetchall()
        result_blue_bot = result_blue_bot.fetchall()
        result_red_bot = result_red_bot.fetchall()
        result_blue_sup = result_blue_sup.fetchall()
        result_red_sup = result_red_sup.fetchall()
        # Process blue side results
        for row in result_blue_top:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_top:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        for row in result_blue_jg:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_jg:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]
        for row in result_blue_mid:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_mid:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]
    
        for row in result_blue_bot:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_bot:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]
        
        for row in result_blue_sup:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_sup:
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

#most popular rune in across all lanes
def get_rune_opponent(engine, champ, opponent):
    sql_blue_top= """
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
    sql_red_top = """
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
    sql_blue_jg = """
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
    sql_red_jg = """
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
    sql_blue_mid = """
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
    sql_red_mid = """
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
    sql_blue_bot = """
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
    sql_red_bot = """
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
    sql_blue_sup = """
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
    sql_red_sup = """
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
        result_blue_top = connection.execute(text(sql_blue_top), {
            "champ": champ,
            "opponent": opponent
        })
        result_red_top = connection.execute(text(sql_red_top), {
            "champ": champ,
            "opponent": opponent
        })
        result_blue_jg = connection.execute(text(sql_blue_jg), {
            "champ": champ,
            "opponent": opponent
        })
        result_red_jg = connection.execute(text(sql_red_jg), {
            "champ": champ,
            "opponent": opponent
        })
        result_blue_mid = connection.execute(text(sql_blue_mid), {
            "champ": champ,
            "opponent": opponent
        })
        result_red_mid = connection.execute(text(sql_red_mid), {
            "champ": champ,
            "opponent": opponent
        })
        result_blue_bot = connection.execute(text(sql_blue_bot), {
            "champ": champ,
            "opponent": opponent
        })
        result_red_bot = connection.execute(text(sql_red_bot), {
            "champ": champ,
            "opponent": opponent
        })
        result_blue_sup = connection.execute(text(sql_blue_sup), {
            "champ": champ,
            "opponent": opponent
        })
        result_red_sup = connection.execute(text(sql_red_sup), {
            "champ": champ,
            "opponent": opponent
        })

         # Initialize a dictionary to accumulate rune counts
        rune_combinations = defaultdict(int)
        result_blue_top = result_blue_top.fetchall()
        result_red_top = result_red_top.fetchall()
        result_blue_jg = result_blue_jg.fetchall()
        result_red_jg = result_red_jg.fetchall()
        result_blue_mid = result_blue_mid.fetchall()
        result_red_mid = result_red_mid.fetchall()
        result_blue_bot = result_blue_bot.fetchall()
        result_red_bot = result_red_bot.fetchall()
        result_blue_sup = result_blue_sup.fetchall()
        result_red_sup = result_red_sup.fetchall()
        # Process blue side results
        for row in result_blue_top:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_top:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        for row in result_blue_jg:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_jg:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]
        for row in result_blue_mid:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_mid:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]
    
        for row in result_blue_bot:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_bot:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]
        
        for row in result_blue_sup:
            rune_combo = (row[0], row[1], row[2], row[3], row[4], row[5])
            rune_combinations[rune_combo] += row[6]

        # Process red side results
        for row in result_red_sup:
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
        
def model_rune_data(engine):
    sql = """
        SELECT
        bluetop_champ AS champion,
        bluetop_rune0 AS rune0_used,
        bluetop_rune1 AS rune1_used,
        bluetop_rune2 AS rune2_used,
        bluetop_rune3 AS rune3_used,
        bluetop_rune4 AS rune4_used,
        bluetop_rune5 AS rune5_used,
        redtop_champ AS opponent,
        0 as lane
    FROM highelo_matches
    UNION ALL
    SELECT
        bluejg_champ AS champion,
        bluejg_rune0 AS rune0_used,
        bluejg_rune1 AS rune1_used,
        bluejg_rune2 AS rune2_used,
        bluejg_rune3 AS rune3_used,
        bluejg_rune4 AS rune4_used,
        bluejg_rune5 AS rune5_used,
        redjg_champ AS opponent,
        1 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluemid_champ AS champion,
        bluemid_rune0 AS rune0_used,
        bluemid_rune1 AS rune1_used,
        bluemid_rune2 AS rune2_used,
        bluemid_rune3 AS rune3_used,
        bluemid_rune4 AS rune4_used,
        bluemid_rune5 AS rune5_used,
        redmid_champ AS opponent,
        2 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluebot_champ AS champion,
        bluebot_rune0 AS rune0_used,
        bluebot_rune1 AS rune1_used,
        bluebot_rune2 AS rune2_used,
        bluebot_rune3 AS rune3_used,
        bluebot_rune4 AS rune4_used,
        bluebot_rune5 AS rune5_used,
        redbot_champ AS opponent,
        3 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluesup_champ AS champion,
        bluesup_rune0 AS rune0_used,
        bluesup_rune1 AS rune1_used,
        bluesup_rune2 AS rune2_used,
        bluesup_rune3 AS rune3_used,
        bluesup_rune4 AS rune4_used,
        bluesup_rune5 AS rune5_used,
        redsup_champ AS opponent,
        4 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redtop_champ AS champion,
        redtop_rune0 AS rune0_used,
        redtop_rune1 AS rune1_used,
        redtop_rune2 AS rune2_used,
        redtop_rune3 AS rune3_used,
        redtop_rune4 AS rune4_used,
        redtop_rune5 AS rune5_used,
        bluetop_champ AS opponent,
        0 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redjg_champ AS champion,
        redjg_rune0 AS rune0_used,
        redjg_rune1 AS rune1_used,
        redjg_rune2 AS rune2_used,
        redjg_rune3 AS rune3_used,
        redjg_rune4 AS rune4_used,
        redjg_rune5 AS rune5_used,
        bluejg_champ AS opponent,
        1 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redmid_champ AS champion,
        redmid_rune0 AS rune0_used,
        redmid_rune1 AS rune1_used,
        redmid_rune2 AS rune2_used,
        redmid_rune3 AS rune3_used,
        redmid_rune4 AS rune4_used,
        redmid_rune5 AS rune5_used,
        bluemid_champ AS opponent,
        2 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redbot_champ AS champion,
        redbot_rune0 AS rune0_used,
        redbot_rune1 AS rune1_used,
        redbot_rune2 AS rune2_used,
        redbot_rune3 AS rune3_used,
        redbot_rune4 AS rune4_used,
        redbot_rune5 AS rune5_used,
        bluebot_champ AS opponent,
        3 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redsup_champ AS champion,
        redsup_rune0 AS rune0_used,
        redsup_rune1 AS rune1_used,
        redsup_rune2 AS rune2_used,
        redsup_rune3 AS rune3_used,
        redsup_rune4 AS rune4_used,
        redsup_rune5 AS rune5_used,
        bluesup_champ AS opponent,
        4 as lane
    FROM highelo_matches;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), {
        })
        results = result.fetchall()
        return results
    


def final_rune_data(engine):
    # sql = """
    #     SELECT
    #     bluetop_champ AS champion,
    #     CONCAT(bluetop_rune0, '-', bluetop_rune1, '-', bluetop_rune2, '-', bluetop_rune3, '-', bluetop_rune4, '-', bluetop_rune5) AS rune_set_used,
    #     redtop_champ AS opponent,
    #     0 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     bluejg_champ AS champion,
    #     CONCAT(bluejg_rune0, '-', bluejg_rune1, '-', bluejg_rune2, '-', bluejg_rune3, '-', bluejg_rune4, '-', bluejg_rune5) AS rune_set_used,
    #     redjg_champ AS opponent,
    #     1 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     bluemid_champ AS champion,
    #     CONCAT(bluemid_rune0, '-', bluemid_rune1, '-', bluemid_rune2, '-', bluemid_rune3, '-', bluemid_rune4, '-', bluemid_rune5) AS rune_set_used,
    #     redmid_champ AS opponent,
    #     2 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     bluebot_champ AS champion,
    #     CONCAT(bluebot_rune0, '-', bluebot_rune1, '-', bluebot_rune2, '-', bluebot_rune3, '-', bluebot_rune4, '-', bluebot_rune5) AS rune_set_used,
    #     redbot_champ AS opponent,
    #     3 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     bluesup_champ AS champion,
    #     CONCAT(bluesup_rune0, '-', bluesup_rune1, '-', bluesup_rune2, '-', bluesup_rune3, '-', bluesup_rune4, '-', bluesup_rune5) AS rune_set_used,
    #     redsup_champ AS opponent,
    #     4 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     redtop_champ AS champion,
    #     CONCAT(redtop_rune0, '-', redtop_rune1, '-', redtop_rune2, '-', redtop_rune3, '-', redtop_rune4, '-', redtop_rune5) AS rune_set_used,
    #     bluetop_champ AS opponent,
    #     0 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     redjg_champ AS champion,
    #     CONCAT(redjg_rune0, '-', redjg_rune1, '-', redjg_rune2, '-', redjg_rune3, '-', redjg_rune4, '-', redjg_rune5) AS rune_set_used,
    #     bluejg_champ AS opponent,
    #     1 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     redmid_champ AS champion,
    #     CONCAT(redmid_rune0, '-', redmid_rune1, '-', redmid_rune2, '-', redmid_rune3, '-', redmid_rune4, '-', redmid_rune5) AS rune_set_used,
    #     bluemid_champ AS opponent,
    #     2 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     redbot_champ AS champion,
    #     CONCAT(redbot_rune0, '-', redbot_rune1, '-', redbot_rune2, '-', redbot_rune3, '-', redbot_rune4, '-', redbot_rune5) AS rune_set_used,
    #     bluebot_champ AS opponent,
    #     3 AS lane
    # FROM highelo_matches
    # UNION ALL
    # SELECT
    #     redsup_champ AS champion,
    #     CONCAT(redsup_rune0, '-', redsup_rune1, '-', redsup_rune2, '-', redsup_rune3, '-', redsup_rune4, '-', redsup_rune5) AS rune_set_used,
    #     bluesup_champ AS opponent,
    #     4 AS lane
    # FROM highelo_matches;

    # """
    sql = """
        SELECT
        bluetop_champ AS champion,
        bluetop_rune0 AS rune0_used,
        bluetop_rune1 AS rune1_used,
        bluetop_rune2 AS rune2_used,
        bluetop_rune3 AS rune3_used,
        bluetop_rune4 AS rune4_used,
        bluetop_rune5 AS rune5_used,
        redtop_champ AS opponent,
        0 as lane
    FROM highelo_matches
    UNION ALL
    SELECT
        bluejg_champ AS champion,
        bluejg_rune0 AS rune0_used,
        bluejg_rune1 AS rune1_used,
        bluejg_rune2 AS rune2_used,
        bluejg_rune3 AS rune3_used,
        bluejg_rune4 AS rune4_used,
        bluejg_rune5 AS rune5_used,
        redjg_champ AS opponent,
        1 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluemid_champ AS champion,
        bluemid_rune0 AS rune0_used,
        bluemid_rune1 AS rune1_used,
        bluemid_rune2 AS rune2_used,
        bluemid_rune3 AS rune3_used,
        bluemid_rune4 AS rune4_used,
        bluemid_rune5 AS rune5_used,
        redmid_champ AS opponent,
        2 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluebot_champ AS champion,
        bluebot_rune0 AS rune0_used,
        bluebot_rune1 AS rune1_used,
        bluebot_rune2 AS rune2_used,
        bluebot_rune3 AS rune3_used,
        bluebot_rune4 AS rune4_used,
        bluebot_rune5 AS rune5_used,
        redbot_champ AS opponent,
        3 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        bluesup_champ AS champion,
        bluesup_rune0 AS rune0_used,
        bluesup_rune1 AS rune1_used,
        bluesup_rune2 AS rune2_used,
        bluesup_rune3 AS rune3_used,
        bluesup_rune4 AS rune4_used,
        bluesup_rune5 AS rune5_used,
        redsup_champ AS opponent,
        4 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redtop_champ AS champion,
        redtop_rune0 AS rune0_used,
        redtop_rune1 AS rune1_used,
        redtop_rune2 AS rune2_used,
        redtop_rune3 AS rune3_used,
        redtop_rune4 AS rune4_used,
        redtop_rune5 AS rune5_used,
        bluetop_champ AS opponent,
        0 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redjg_champ AS champion,
        redjg_rune0 AS rune0_used,
        redjg_rune1 AS rune1_used,
        redjg_rune2 AS rune2_used,
        redjg_rune3 AS rune3_used,
        redjg_rune4 AS rune4_used,
        redjg_rune5 AS rune5_used,
        bluejg_champ AS opponent,
        1 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redmid_champ AS champion,
        redmid_rune0 AS rune0_used,
        redmid_rune1 AS rune1_used,
        redmid_rune2 AS rune2_used,
        redmid_rune3 AS rune3_used,
        redmid_rune4 AS rune4_used,
        redmid_rune5 AS rune5_used,
        bluemid_champ AS opponent,
        2 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redbot_champ AS champion,
        redbot_rune0 AS rune0_used,
        redbot_rune1 AS rune1_used,
        redbot_rune2 AS rune2_used,
        redbot_rune3 AS rune3_used,
        redbot_rune4 AS rune4_used,
        redbot_rune5 AS rune5_used,
        bluebot_champ AS opponent,
        3 as lane
    FROM highelo_matches

    UNION ALL

    SELECT
        redsup_champ AS champion,
        redsup_rune0 AS rune0_used,
        redsup_rune1 AS rune1_used,
        redsup_rune2 AS rune2_used,
        redsup_rune3 AS rune3_used,
        redsup_rune4 AS rune4_used,
        redsup_rune5 AS rune5_used,
        bluesup_champ AS opponent,
        4 as lane
    FROM highelo_matches;
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql), {
        })
        results = result.fetchall()
        champ_map = final_champ_map()
        actual_data = []
        for row in results:
            champion_name = row[0]
            champion_type = champ_map[int(champion_name)]["type"]
            if champion_type == "melee":
                champion_type = 0
            elif champion_type == "ranged":
                champion_type = 1
            else:
                champion_type = 3
            champion_damage = champ_map[int(champion_name)]["damage"]
            if champion_damage == "AD":
                champion_damage = 0
            elif champion_damage == "AP":
                champion_damage = 1
            else:
                champion_damage = 3
            champion_role = champ_map[int(champion_name)]["role"]
            if champion_role == "tank":
                champion_role = 0
            elif champion_role == "bruiser":
                champion_role = 1
            elif champion_role == "assassin":
                champion_role = 2
            elif champion_role == "marksman":
                champion_role = 3
            elif champion_role == "mage":
                champion_role = 4
            elif champion_role == "support":
                champion_role = 5
            elif champion_role == "enchanter":
                champion_role = 6
            else:
                champion_role = 7
            #rune_set = row[1]
            #lane = row[3]
            lane = row[8]
            #opponent_name = row[2]
            opponent_name = row[7]
            opponent_type = champ_map[int(opponent_name)]["type"]
            if opponent_type == "melee":
                opponent_type = 0
            elif opponent_type == "ranged":
                opponent_type = 1
            else:
                opponent_type = 3
            opponent_damage = champ_map[int(opponent_name)]["damage"]
            if opponent_damage == "AD":
                opponent_damage = 0
            elif opponent_damage == "AP":
                opponent_damage = 1
            else:
                opponent_damage = 3
            opponent_role = champ_map[int(opponent_name)]["role"]
            if opponent_role == "tank":
                opponent_role = 0
            elif opponent_role == "bruiser":
                opponent_role = 1
            elif opponent_role == "assassin":
                opponent_role = 2
            elif opponent_role == "marksman":
                opponent_role = 3
            elif opponent_role == "mage":
                opponent_role = 4
            elif opponent_role == "support":
                opponent_role = 5
            elif opponent_role == "enchanter":
                opponent_role = 6
            else:
                opponent_role = 7
            rune0 = row[1]
            rune1 = row[2]
            rune2 = row[3]
            rune3 = row[4]
            rune4 = row[5]
            rune5 = row[6]
            actual_data.append({
                'champion': int(champion_name),
                'champion_type': champion_type,
                'champion_damage': champion_damage,
                'champion_role': champion_role,
                'rune0': int(rune0),
                'rune1': int(rune1),
                'rune2': int(rune2),
                'rune3': int(rune3),
                'rune4': int(rune4),
                'rune5': int(rune5),
                'lane': lane,
                'opponent_name': int(opponent_name),
                'opponent_type': opponent_type,
                'opponent_damage': opponent_damage,
                'opponent_role': opponent_role
            })

        return actual_data
    
def champ_mapping():
    champion_attributes = {
    "Aatrox": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Ahri": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Akali": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Akshan": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Alistar": {"type": "melee", "damage": "AD", "role": "support"},
    "Amumu": {"type": "melee", "damage": "AP", "role": "tank"},
    "Anivia": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Annie": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Aphelios": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Ashe": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Aurelion Sol": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Aurora": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Azir": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Bard": {"type": "ranged", "damage": "AP", "role": "support"},
    "Bel'Veth": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Blitzcrank": {"type": "melee", "damage": "AD", "role": "support"},
    "Brand": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Braum": {"type": "melee", "damage": "AD", "role": "support"},
    "Briar": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Caitlyn": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Camille": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Cassiopeia": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Chogath": {"type": "melee", "damage": "AP", "role": "tank"},
    "Corki": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Darius": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Diana": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Draven": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Dr. Mundo": {"type": "melee", "damage": "AD/AP", "role": "tank"},
    "Ekko": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Elise": {"type": "ranged/melee", "damage": "AP", "role": "assassin"},
    "Evelynn": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Ezreal": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Fiddlesticks": {"type": "ranged", "damage": "AP", "role": "assassin"},
    "Fiora": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Fizz": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Galio": {"type": "melee", "damage": "AP", "role": "mage"},
    "Gangplank": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Garen": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Gnar": {"type": "ranged/melee", "damage": "AD", "role": "bruiser"},
    "Gragas": {"type": "melee", "damage": "AP", "role": "tank/mage"},
    "Graves": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Gwen": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Hecarim": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Heimerdinger": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Hwei": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Illaoi": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Irelia": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Ivern": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Janna": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Jarvan IV": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Jax": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Jayce": {"type": "ranged/melee", "damage": "AD", "role": "bruiser"},
    "Jhin": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Jinx": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Kai'Sa": {"type": "ranged", "damage": "AD/AP", "role": "marksman"},
    "Kalista": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Karma": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Karthus": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Kassadin": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Katarina": {"type": "melee", "damage": "AP", "role": "assassin"},
    "Kayle": {"type": "ranged/melee", "damage": "AD/AP", "role": "marksman"},
    "Kayn": {"type": "melee", "damage": "AD", "role": "assassin/bruiser"},
    "Kennen": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Kha'Zix": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Kindred": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Kled": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Kog'Maw": {"type": "ranged", "damage": "AD/AP", "role": "marksman"},
    "K'Sante": {"type": "melee", "damage": "AD", "role": "tank"},
    "LeBlanc": {"type": "ranged", "damage": "AP", "role": "assassin"},
    "Lee Sin": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Leona": {"type": "melee", "damage": "AD", "role": "support"},
    "Lillia": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Lissandra": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Lucian": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Lulu": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Lux": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Malphite": {"type": "melee", "damage": "AP", "role": "tank"},
    "Malzahar": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Maokai": {"type": "melee", "damage": "AP", "role": "tank"},
    "Master Yi": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Milio": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Miss Fortune": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Mordekaiser": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Morgana": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Naafiri": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Nami": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Nasus": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Nautilus": {"type": "melee", "damage": "AP", "role": "support"},
    "Neeko": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Nidalee": {"type": "ranged/melee", "damage": "AP", "role": "assassin"},
    "Nilah": {"type": "melee", "damage": "AD", "role": "marksman"},
    "Nocturne": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Nunu & Willump": {"type": "melee", "damage": "AP", "role": "tank"},
    "Olaf": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Orianna": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Ornn": {"type": "melee", "damage": "AD/AP", "role": "tank"},
    "Pantheon": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Poppy": {"type": "melee", "damage": "AD", "role": "tank"},
    "Pyke": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Qiyana": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Quinn": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Rakan": {"type": "melee", "damage": "AP", "role": "support"},
    "Rammus": {"type": "melee", "damage": "AD", "role": "tank"},
    "Rek'Sai": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Rell": {"type": "melee", "damage": "AD", "role": "support"},
    "Renata Glasc": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Renekton": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Rengar": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Riven": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Rumble": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Ryze": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Samira": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Sejuani": {"type": "melee", "damage": "AP", "role": "tank"},
    "Senna": {"type": "ranged", "damage": "AD", "role": "marksman/enchanter"},
    "Seraphine": {"type": "ranged", "damage": "AP", "role": "mage/enhanter"},
    "Sett": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Shaco": {"type": "melee", "damage": "AD/AP", "role": "assassin"},
    "Shen": {"type": "melee", "damage": "AD", "role": "tank"},
    "Shyvana": {"type": "melee", "damage": "AD/AP", "role": "bruiser"},
    "Singed": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Sion": {"type": "melee", "damage": "AD", "role": "tank"},
    "Sivir": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Skarner": {"type": "melee", "damage": "AP", "role": "tank"},
    "Smolder": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Sona": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Soraka": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Swain": {"type": "ranged", "damage": "AP", "role": "bruiser"},
    "Sylas": {"type": "melee", "damage": "AP", "role": "bruiser"},
    "Syndra": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Tahm Kench": {"type": "melee", "damage": "AD/AP", "role": "tank"},
    "Taliyah": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Talon": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Taric": {"type": "melee", "damage": "AP", "role": "support"},
    "Teemo": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Thresh": {"type": "melee", "damage": "AP", "role": "support"},
    "Tristana": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Trundle": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Tryndamere": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Twisted Fate": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Twitch": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Udyr": {"type": "melee", "damage": "AD/AP", "role": "bruiser"},
    "Urgot": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Varus": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Vayne": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Veigar": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vel'Koz": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vex": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vi": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Viego": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Viktor": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Vladimir": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Volibear": {"type": "melee", "damage": "AD/AP", "role": "bruiser"},
    "Warwick": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Wukong": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Xayah": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Xerath": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Xin Zhao": {"type": "ranged", "damage": "AD", "role": "bruiser"},
    "Yasuo": {"type": "melee", "damage": "AD", "role": "marksman"},
    "Yone": {"type": "melee", "damage": "AD", "role": "marksman"},
    "Yorick": {"type": "melee", "damage": "AD", "role": "bruiser"},
    "Yuumi": {"type": "ranged", "damage": "AP", "role": "enchanter"},
    "Zac": {"type": "melee", "damage": "AP", "role": "tank"},
    "Zed": {"type": "melee", "damage": "AD", "role": "assassin"},
    "Zeri": {"type": "ranged", "damage": "AD", "role": "marksman"},
    "Ziggs": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Zilean": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Zoe": {"type": "ranged", "damage": "AP", "role": "mage"},
    "Zyra": {"type": "ranged", "damage": "AP", "role": "mage"}
    }
    return champion_attributes

def final_champ_map():
    champion_attributes = {
    266: {"name": "Aatrox", "type": "melee", "damage": "AD", "role": "bruiser"},
    103: {"name": "Ahri", "type": "ranged", "damage": "AP", "role": "mage"},
    84: {"name": "Akali", "type": "melee", "damage": "AP", "role": "assassin"},
    166: {"name": "Akshan", "type": "ranged", "damage": "AD", "role": "marksman"},
    12: {"name": "Alistar", "type": "melee", "damage": "AD", "role": "support"},
    32: {"name": "Amumu", "type": "melee", "damage": "AP", "role": "tank"},
    34: {"name": "Anivia", "type": "ranged", "damage": "AP", "role": "mage"},
    1: {"name": "Annie", "type": "ranged", "damage": "AP", "role": "mage"},
    523: {"name": "Aphelios", "type": "ranged", "damage": "AD", "role": "marksman"},
    22: {"name": "Ashe", "type": "ranged", "damage": "AD", "role": "marksman"},
    136: {"name": "Aurelion Sol", "type": "ranged", "damage": "AP", "role": "mage"},
    893: {"name": "Aurora", "type": "ranged", "damage": "AP", "role": "mage"},
    268: {"name": "Azir", "type": "ranged", "damage": "AP", "role": "mage"},
    432: {"name": "Bard", "type": "ranged", "damage": "AP", "role": "support"},
    200: {"name": "Bel'Veth", "type": "melee", "damage": "AD", "role": "bruiser"},
    53: {"name": "Blitzcrank", "type": "melee", "damage": "AD", "role": "support"},
    63: {"name": "Brand", "type": "ranged", "damage": "AP", "role": "mage"},
    201: {"name": "Braum", "type": "melee", "damage": "AD", "role": "support"},
    233: {"name": "Briar", "type": "melee", "damage": "AD", "role": "bruiser"},
    51: {"name": "Caitlyn", "type": "ranged", "damage": "AD", "role": "marksman"},
    164: {"name": "Camille", "type": "melee", "damage": "AD", "role": "bruiser"},
    69: {"name": "Cassiopeia", "type": "ranged", "damage": "AP", "role": "mage"},
    31: {"name": "Chogath", "type": "melee", "damage": "AP", "role": "tank"},
    42: {"name": "Corki", "type": "ranged", "damage": "AD", "role": "marksman"},
    122: {"name": "Darius", "type": "melee", "damage": "AD", "role": "bruiser"},
    131: {"name": "Diana", "type": "melee", "damage": "AP", "role": "assassin"},
    119: {"name": "Draven", "type": "ranged", "damage": "AD", "role": "marksman"},
    36: {"name": "Dr. Mundo", "type": "melee", "damage": "AD/AP", "role": "tank"},
    245: {"name": "Ekko", "type": "melee", "damage": "AP", "role": "assassin"},
    60: {"name": "Elise", "type": "ranged/melee", "damage": "AP", "role": "assassin"},
    28: {"name": "Evelynn", "type": "melee", "damage": "AP", "role": "assassin"},
    81: {"name": "Ezreal", "type": "ranged", "damage": "AD", "role": "marksman"},
    9: {"name": "Fiddlesticks", "type": "ranged", "damage": "AP", "role": "assassin"},
    114: {"name": "Fiora", "type": "melee", "damage": "AD", "role": "bruiser"},
    105: {"name": "Fizz", "type": "melee", "damage": "AP", "role": "assassin"},
    3: {"name": "Galio", "type": "melee", "damage": "AP", "role": "mage"},
    41: {"name": "Gangplank", "type": "melee", "damage": "AD", "role": "bruiser"},
    86: {"name": "Garen", "type": "melee", "damage": "AD", "role": "bruiser"},
    150: {"name": "Gnar", "type": "ranged/melee", "damage": "AD", "role": "bruiser"},
    79: {"name": "Gragas", "type": "melee", "damage": "AP", "role": "tank/mage"},
    104: {"name": "Graves", "type": "ranged", "damage": "AD", "role": "marksman"},
    887: {"name": "Gwen", "type": "melee", "damage": "AP", "role": "bruiser"},
    120: {"name": "Hecarim", "type": "melee", "damage": "AD", "role": "bruiser"},
    74: {"name": "Heimerdinger", "type": "ranged", "damage": "AP", "role": "mage"},
    910: {"name": "Hwei", "type": "ranged", "damage": "AP", "role": "mage"},
    420: {"name": "Illaoi", "type": "melee", "damage": "AD", "role": "bruiser"},
    39: {"name": "Irelia", "type": "melee", "damage": "AD", "role": "bruiser"},
    427: {"name": "Ivern", "type": "ranged", "damage": "AP", "role": "enchanter"},
    40: {"name": "Janna", "type": "ranged", "damage": "AP", "role": "enchanter"},
    59: {"name": "Jarvan IV", "type": "melee", "damage": "AD", "role": "bruiser"},
    24: {"name": "Jax", "type": "melee", "damage": "AD", "role": "bruiser"},
    126: {"name": "Jayce", "type": "ranged/melee", "damage": "AD", "role": "bruiser"},
    202: {"name": "Jhin", "type": "ranged", "damage": "AD", "role": "marksman"},
    222: {"name": "Jinx", "type": "ranged", "damage": "AD", "role": "marksman"},
    145: {"name": "Kai'Sa", "type": "ranged", "damage": "AD/AP", "role": "marksman"},
    429: {"name": "Kalista", "type": "ranged", "damage": "AD", "role": "marksman"},
    43: {"name": "Karma", "type": "ranged", "damage": "AP", "role": "enchanter"},
    30: {"name": "Karthus", "type": "ranged", "damage": "AP", "role": "mage"},
    38: {"name": "Kassadin", "type": "melee", "damage": "AP", "role": "mage"},
    55: {"name": "Katarina", "type": "melee", "damage": "AP", "role": "assassin"},
    10: {"name": "Kayle", "type": "ranged/melee", "damage": "AD/AP", "role": "marksman"},
    141: {"name": "Kayn", "type": "melee", "damage": "AD", "role": "assassin/bruiser"},
    85: {"name": "Kennen", "type": "ranged", "damage": "AP", "role": "mage"},
    121: {"name": "Kha'Zix", "type": "melee", "damage": "AD", "role": "assassin"},
    240: {"name": "Kled", "type": "melee", "damage": "AD", "role": "bruiser"},
    96: {"name": "Kog'Maw", "type": "ranged", "damage": "AD/AP", "role": "marksman"},
    127: {"name": "Lissandra", "type": "ranged", "damage": "AP", "role": "mage"},
    117: {"name": "Lulu", "type": "ranged", "damage": "AP", "role": "enchanter"},
    99: {"name": "Lux", "type": "ranged", "damage": "AP", "role": "mage"},
    54: {"name": "Malphite", "type": "melee", "damage": "AD/AP", "role": "tank"},
    90: {"name": "Malzahar", "type": "ranged", "damage": "AP", "role": "mage"},
    57: {"name": "Maokai", "type": "melee", "damage": "AP", "role": "tank"},
    82: {"name": "Mordekaiser", "type": "melee", "damage": "AP", "role": "bruiser"},
    25: {"name": "Morgana", "type": "ranged", "damage": "AP", "role": "mage"},
    267: {"name": "Nami", "type": "ranged", "damage": "AP", "role": "enchanter"},
    75: {"name": "Nasus", "type": "melee", "damage": "AD", "role": "bruiser"},
    111: {"name": "Nautilus", "type": "melee", "damage": "AD", "role": "tank"},
    518: {"name": "Neeko", "type": "ranged", "damage": "AP", "role": "mage"},
    76: {"name": "Nidalee", "type": "ranged/melee", "damage": "AD/AP", "role": "assassin"},
    56: {"name": "Nocturne", "type": "melee", "damage": "AD", "role": "assassin"},
    20: {"name": "Nunu & Willump", "type": "melee", "damage": "AP", "role": "tank"},
    2: {"name": "Olaf", "type": "melee", "damage": "AD", "role": "bruiser"},
    61: {"name": "Orianna", "type": "ranged", "damage": "AP", "role": "mage"},
    516: {"name": "Ornn", "type": "melee", "damage": "AD/AP", "role": "tank"},
    80: {"name": "Pantheon", "type": "melee", "damage": "AD", "role": "bruiser"},
    78: {"name": "Poppy", "type": "melee", "damage": "AD", "role": "tank"},
    555: {"name": "Pyke", "type": "melee", "damage": "AD", "role": "assassin/support"},
    246: {"name": "Qiyana", "type": "melee", "damage": "AD", "role": "assassin"},
    133: {"name": "Quinn", "type": "ranged", "damage": "AD", "role": "marksman"},
    497: {"name": "Rakan", "type": "melee", "damage": "AP", "role": "support"},
    33: {"name": "Rammus", "type": "melee", "damage": "AD", "role": "tank"},
    421: {"name": "Rek'Sai", "type": "melee", "damage": "AD", "role": "bruiser"},
    58: {"name": "Renekton", "type": "melee", "damage": "AD", "role": "bruiser"},
    92: {"name": "Riven", "type": "melee", "damage": "AD", "role": "bruiser"},
    68: {"name": "Rumble", "type": "melee", "damage": "AP", "role": "bruiser"},
    13: {"name": "Ryze", "type": "ranged", "damage": "AP", "role": "mage"},
    360: {"name": "Samira", "type": "ranged", "damage": "AD", "role": "marksman"},
    113: {"name": "Sejuani", "type": "melee", "damage": "AD/AP", "role": "tank"},
    147: {"name": "Seraphine", "type": "ranged", "damage": "AP", "role": "mage"},
    875: {"name": "Sett", "type": "melee", "damage": "AD", "role": "bruiser"},
    35: {"name": "Shaco", "type": "melee/ranged", "damage": "AD/AP", "role": "assassin"},
    98: {"name": "Shen", "type": "melee", "damage": "AD", "role": "tank"},
    102: {"name": "Shyvana", "type": "melee", "damage": "AD/AP", "role": "bruiser"},
    14: {"name": "Sion", "type": "melee", "damage": "AD/AP", "role": "tank"},
    37: {"name": "Sona", "type": "ranged", "damage": "AP", "role": "enchanter"},
    16: {"name": "Soraka", "type": "ranged", "damage": "AP", "role": "support"},
    50: {"name": "Swain", "type": "ranged", "damage": "AP", "role": "mage"},
    517: {"name": "Sylas", "type": "melee", "damage": "AD/AP", "role": "bruiser"},
    223: {"name": "Tahm Kench", "type": "melee", "damage": "AD", "role": "tank"},
    163: {"name": "Taliyah", "type": "ranged", "damage": "AP", "role": "mage"},
    91: {"name": "Talon", "type": "melee", "damage": "AD", "role": "assassin"},
    44: {"name": "Taric", "type": "melee", "damage": "AD", "role": "support"},
    17: {"name": "Teemo", "type": "ranged", "damage": "AD/AP", "role": "marksman"},
    412: {"name": "Thresh", "type": "melee", "damage": "AD", "role": "support"},
    48: {"name": "Trundle", "type": "melee", "damage": "AD", "role": "bruiser"},
    23: {"name": "Tryndamere", "type": "melee", "damage": "AD", "role": "bruiser"},
    4: {"name": "Twisted Fate", "type": "ranged", "damage": "AP", "role": "mage"},
    77: {"name": "Udyr", "type": "melee", "damage": "AD/AP", "role": "bruiser"},
    6: {"name": "Urgot", "type": "melee", "damage": "AD", "role": "bruiser"},
    110: {"name": "Varus", "type": "ranged", "damage": "AD", "role": "marksman"},
    67: {"name": "Vayne", "type": "ranged", "damage": "AD", "role": "marksman"},
    45: {"name": "Veigar", "type": "ranged", "damage": "AP", "role": "mage"},
    161: {"name": "Vel'Koz", "type": "ranged", "damage": "AP", "role": "mage"},
    711: {"name": "Vex", "type": "ranged", "damage": "AP", "role": "mage"},
    112: {"name": "Viktor", "type": "ranged", "damage": "AP", "role": "mage"},
    8: {"name": "Vladimir", "type": "ranged", "damage": "AP", "role": "mage"},
    106: {"name": "Volibear", "type": "melee", "damage": "AD", "role": "tank"},
    154: {"name": "Zac", "type": "melee", "damage": "AP", "role": "tank"},
    221: {"name": "Zeri", "type": "ranged", "damage": "AD", "role": "marksman"},
    26: {"name": "Zilean", "type": "ranged", "damage": "AP", "role": "mage"},
    142: {"name": "Zoe", "type": "ranged", "damage": "AP", "role": "mage"},
    143: {"name": "Zyra", "type": "ranged", "damage": "AP", "role": "mage"},
    203: {"name": "Kindred", "type": "ranged", "damage": "AD", "role": "marksman"},
    897: {"name": "K'Sante", "type": "melee", "damage": "AD", "role": "tank"},
    7: {"name": "LeBlanc", "type": "ranged", "damage": "AP", "role": "assassin"},
    64: {"name": "Lee Sin", "type": "melee", "damage": "AD", "role": "bruiser"},
    89: {"name": "Leona", "type": "melee", "damage": "AP", "role": "support"},
    876: {"name": "Lillia", "type": "melee", "damage": "AP", "role": "bruiser"},
    236: {"name": "Lucian", "type": "ranged", "damage": "AD", "role": "marksman"},
    11: {"name": "Master Yi", "type": "melee", "damage": "AD", "role": "assassin"},
    902: {"name": "Milio", "type": "ranged", "damage": "AP", "role": "enchanter"},
    21: {"name": "Miss Fortune", "type": "ranged", "damage": "AD", "role": "marksman"},
    950: {"name": "Naafiri", "type": "melee", "damage": "AD", "role": "assassin"},
    895: {"name": "Nilah", "type": "melee", "damage": "AD", "role": "marksman"},
    526: {"name": "Rell", "type": "melee", "damage": "AP", "role": "tank"},
    888: {"name": "Renata Glasc", "type": "ranged", "damage": "AP", "role": "enchanter"},
    107: {"name": "Rengar", "type": "melee", "damage": "AD", "role": "assassin"},
    235: {"name": "Senna", "type": "ranged", "damage": "AD/AP", "role": "marksman/support"},
    27: {"name": "Singed", "type": "melee", "damage": "AP", "role": "bruiser"},
    15: {"name": "Sivir", "type": "ranged", "damage": "AD", "role": "marksman"},
    72: {"name": "Skarner", "type": "melee", "damage": "AP", "role": "tank"},
    901: {"name": "Smolder", "type": "melee", "damage": "AD", "role": "marksman"},
    134: {"name": "Syndra", "type": "ranged", "damage": "AP", "role": "mage"},
    18: {"name": "Tristana", "type": "ranged", "damage": "AD", "role": "marksman"},
    29: {"name": "Twitch", "type": "ranged", "damage": "AD", "role": "marksman"},
    254: {"name": "Vi", "type": "melee", "damage": "AD", "role": "bruiser"},
    234: {"name": "Viego", "type": "melee", "damage": "AD", "role": "bruiser"},
    19: {"name": "Warwick", "type": "melee", "damage": "AD", "role": "bruiser"},
    62: {"name": "Wukong", "type": "melee", "damage": "AD", "role": "bruiser"},
    498: {"name": "Xayah", "type": "ranged", "damage": "AD", "role": "marksman"},
    101: {"name": "Xerath", "type": "ranged", "damage": "AP", "role": "mage"},
    5: {"name": "Xin Zhao", "type": "melee", "damage": "AD", "role": "bruiser"},
    157: {"name": "Yasuo", "type": "melee", "damage": "AD", "role": "marksman"},
    777: {"name": "Yone", "type": "melee", "damage": "AD", "role": "marksman"},
    83: {"name": "Yorick", "type": "melee", "damage": "AD", "role": "bruiser"},
    350: {"name": "Yuumi", "type": "ranged", "damage": "AP", "role": "enchanter"},
    238: {"name": "Zed", "type": "melee", "damage": "AD", "role": "assassin"},
    115: {"name": "Ziggs", "type": "ranged", "damage": "AP", "role": "mage"}
    }

    return champion_attributes
