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