# this files contains functions that clean the data 
# the primary goal of this is to standardize the categorical text columns
# and the abreviations so that when we create the visualizations the groupings are clean
# we also will create additional columns in the tables to use in the visualizations


def standardize_columns(cursor):
    allowed_values = {
        "team": ["a", "b"],
        "pass_rating": ["in", "out"],
        "set_type": ["opposite", "quick", "off_speed", "bic"],
        "serve_type": ["jump", "float"],
        "block_touch": ["yes", "no"],
        "hit_type": ["tip", "roll_shot", "free_ball", "off_speed", "hit", "overpass", "blocked"],
        "win_reason": ["kill", "hit_error", "serve_error", "tool", "ace", "net"],
        "lose_reason": ["kill", "hit_error", "serve_error", "tool", "ace", "net"],
        "winning_team": ["a", "b"]
    }

    for col, values in allowed_values.items():
        sql_values = ",".join(f"'{v}'" for v in values)
        query = f"""
            UPDATE volleyball
            SET {col} = CASE
                WHEN LOWER(TRIM({col})) IN ({sql_values}) THEN LOWER(TRIM({col}))
                ELSE NULL
            END
        """
        cursor.execute(query)

def replace_empty_strings(cursor):
    text_columns = [
        "team", "pass_rating", "set_type", "set_location",
        "hit_type", "block_touch", "serve_type",
        "win_reason", "lose_reason", "winning_team"
    ]

    for col in text_columns:
        query = f"""
            UPDATE volleyball
            SET {col} = NULL
            WHERE {col} IS NOT NULL AND TRIM({col}) = '';
        """
        cursor.execute(query)


def player_aggregates(cursor):
    # create column for kills, errors, hit efficiency
    cursor.execute("""
        ALTER TABLE players 
            ADD COLUMN IF NOT EXISTS total_kills INTEGER ,
            ADD COLUMN IF NOT EXISTS total_hit_errors INTEGER,
            ADD COLUMN IF NOT EXISTS hitting_efficiency NUMERIC
    """)

    # map the player id, to a jersey number and team name
    cursor.execute("""
        WITH player_map AS (
            SELECT player_id, jersey_number, team_name
            FROM players
        )
        -- total kills
        UPDATE players p
        SET total_kills = sub.kills
        FROM (
            SELECT pm.player_id, COUNT(*) AS kills
            FROM volleyball v
            JOIN player_map pm
                ON v.hitter_location = pm.jersey_number
                AND v.team = pm.team_name
            WHERE v.win_reason = 'kill'
            GROUP BY pm.player_id
        ) sub
        WHERE p.player_id = sub.player_id;
    """)

    # total hit errors
    cursor.execute("""
        UPDATE players p
        SET total_hit_errors = sub.errors
        FROM (
            SELECT pm.player_id, COUNT(*) AS errors
            FROM volleyball v
            JOIN players pm
                ON v.hitter_location = pm.jersey_number
                AND v.team = pm.team_name
            WHERE v.win_reason = 'hit_error'
            GROUP BY pm.player_id
        ) sub
        WHERE p.player_id = sub.player_id;
    """)

    # total hits = kills + errors + other hits
    cursor.execute("""
        UPDATE players p
        SET total_hits = sub.hits
        FROM (
            SELECT pm.player_id, COUNT(*) AS hits
            FROM volleyball v
            JOIN players pm
                ON v.hitter_location = pm.jersey_number
                AND v.team = pm.team_name
            WHERE v.hit_type IS NOT NULL
            GROUP BY pm.player_id
        ) sub
        WHERE p.player_id = sub.player_id;
    """)

    # hitting efficiency
    cursor.execute("""
        UPDATE players
        SET hitting_efficiency = CASE
            WHEN total_hits > 0 THEN (total_kills - total_hit_errors)::NUMERIC / total_hits
            ELSE NULL
        END;
    """)


    # hit type percentages
    hit_types = ['tip', 'roll_shot', 'free_ball', 'off_speed', 'hit', 'overpass', 'blocked']
    for ht in hit_types:
        cursor.execute(f"""
            ALTER TABLE players ADD COLUMN IF NOT EXISTS pct_{ht} NUMERIC;
            UPDATE players p
            SET pct_{ht} = sub.cnt::NUMERIC / NULLIF(total_hits, 0)
            FROM (
                SELECT pm.player_id, COUNT(*) AS cnt
                FROM volleyball v
                JOIN players pm
                    ON v.hitter_location = pm.jersey_number
                    AND v.team = pm.team_name
                WHERE v.hit_type = '{ht}'
                GROUP BY pm.player_id
            ) sub
            WHERE p.player_id = sub.player_id;
        """)



def team_aggregates(cursor):
   # add aggregate columns for each of the team tables
    for table in ['team_a', 'team_b']:
        cursor.execute(f"""
            ALTER TABLE {table} 
                ADD COLUMN IF NOT EXISTS total_kills INTEGER ,
                ADD COLUMN IF NOT EXISTS total_hit_errors INTEGER,
                ADD COLUMN IF NOT EXISTS total_hits INTEGER ,
                ADD COLUMN IF NOT EXISTS hitting_efficiency NUMERIC,
                ADD COLUMN IF NOT EXISTS total_service_aces INTEGER,
                ADD COLUMN IF NOT EXISTS total_service_errors INTEGER,
                ADD COLUMN IF NOT EXISTS service_ace_ratio NUMERIC;
        """)
    
    # total kills per team
    for table in ['team_a', 'team_b']:
        cursor.execute(f"""
            UPDATE {table} t
            SET total_kills = sub.kills
            FROM (
                SELECT t.rally_id, COUNT(*) AS kills
                FROM {table} t
                JOIN rallies r ON t.rally_id = r.id
                WHERE r.win_reason = 'kill'
                GROUP BY t.rally_id
            ) sub
            WHERE t.rally_id = sub.rally_id;
        """)

        # total hit errors per team
        cursor.execute(f"""
                UPDATE {table} t
                SET total_hit_errors = sub.errors
                FROM (
                    SELECT t.rally_id, COUNT(*) AS errors
                    FROM {table} t
                    JOIN rallies r ON t.rally_id = r.id
                    WHERE r.win_reason = 'hit_error'
                    GROUP BY t.rally_id
                ) sub
                WHERE t.rally_id = sub.rally_id;
            """)
   
        # total hits per rally per team
        cursor.execute(f"""
            UPDATE {table} t
            SET total_hits = sub.hits
            FROM (
                SELECT t.rally_id, COUNT(*) AS hits
                FROM {table} t
                JOIN rallies r ON t.rally_id = r.id
                WHERE r.hit_type IS NOT NULL
                GROUP BY t.rally_id
            ) sub
            WHERE t.rally_id = sub.rally_id;
        """)

        # team hitting efficiency
        cursor.execute(f"""
            UPDATE {table}
            SET hitting_efficiency = CASE
                WHEN total_hits > 0 THEN (total_kills - total_hit_errors)::NUMERIC / total_hits
                ELSE NULL
            END;
        """)

        # hit type percentages
        hit_types = ['tip', 'roll_shot', 'free_ball', 'off_speed', 'hit', 'overpass', 'blocked']
        for ht in hit_types:
            # add a column in the table for each hit type percentage
            cursor.execute(f"""
                ALTER TABLE {table} ADD COLUMN IF NOT EXISTS pct_{ht} NUMERIC;
            """)

        # calculate percentages
        for ht in hit_types:
            cursor.execute(f"""
                UPDATE {table} t
                SET pct_{ht} = sub.cnt::NUMERIC / NULLIF(total_hits, 0)
                FROM (
                    SELECT t.rally_id, COUNT(*) AS cnt
                    FROM {table} t
                    JOIN rallies r ON t.rally_id = r.id
                    WHERE r.hit_type = '{ht}'
                    GROUP BY t.rally_id
                ) sub
                WHERE t.rally_id = sub.rally_id;
            """)

        # service aces / service errors
        team_code = 'a' if table == 'team_a' else 'b'
        cursor.execute(f"""
            WITH service_counts AS (
                SELECT
                    COUNT(*) AS total_service_aces,
                    COUNT(*) FILTER (WHERE r.win_reason = 'serve_error') AS total_service_errors
                FROM rallies r
                WHERE r.round = 1
                AND r.team = '{team_code}'
                AND r.win_reason IN ('ace', 'serve_error')
            )
            UPDATE {table}
            SET total_service_aces = sc.total_service_aces,
                total_service_errors = sc.total_service_errors,
                service_ace_ratio = CASE 
                                    WHEN sc.total_service_errors > 0 
                                    THEN sc.total_service_aces::NUMERIC / sc.total_service_errors 
                                    ELSE 0 
                                    END
            FROM service_counts sc
            WHERE 1=1;
        """)



