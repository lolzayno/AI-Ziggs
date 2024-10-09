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