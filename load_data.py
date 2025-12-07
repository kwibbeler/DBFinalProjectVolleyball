# this file will load in the data from the csv file and create the table 
# in the class database for storage


def create_table(cursor):
    cursor.execute("DROP TABLE IF EXISTS volleyball")
    cursor.execute("""
        CREATE TABLE volleyball (
            rally integer,
            round integer,
            team text,
            recieve_location integer,
            digger_location integer,
            pass_land_location integer,
            hitter_location integer,
            hit_land_location integer,
            pass_rating text,
            set_type text,
            set_location text,
            hit_type text,
            num_blockers integer,
            block_touch text,
            serve_type text,
            win_reason text,
            lose_reason text,
            winning_team text
        )
    """) 

def bulk_load_csv(connection):
    with open("dataset_full.csv", "r", encoding="utf-8") as f:
        data = f.read()

    # COPY FROM STDIN using pg8000's conn.run()
    connection.run("COPY volleyball FROM STDIN WITH (FORMAT csv, HEADER true)", data)

    print("CSV loaded successfully!")

# this section will create the derived tables from the original table 
def create_derived_tables(cursor):
    # make sure the tables don't already exist in the database
    cursor.execute("DROP TABLE IF EXISTS rallies")
    cursor.execute("DROP TABLE IF EXISTS team_a")
    cursor.execute("DROP TABLE IF EXISTS team_b")
    cursor.execute("DROP TABLE IF EXISTS players")

    # rally table
    cursor.execute(""" 
    CREATE TABLE rallies (
        id SERIAL PRIMARY KEY,
        rally_id INTEGER,          
        team TEXT,
        round INTEGER,
        winning_team TEXT,
        win_reason TEXT,
        lose_reason TEXT,
        receive_location INTEGER,
        pass_land_location INTEGER,
        hitter_location INTEGER,
        hit_land_location INTEGER,
        pass_rating TEXT,
        set_location TEXT,
        num_blockers INTEGER,
        block_touch TEXT,
        serve_type TEXT,
        hit_type TEXT,
        digger_location INTEGER
    );""")

    # team A table
    cursor.execute(""" CREATE TABLE team_a (
        rally_id INTEGER PRIMARY KEY REFERENCES rallies(id),
        team_name TEXT,
        receiver INTEGER,
        digger INTEGER,
        hitter INTEGER
    );
    """)

    # team B table
    cursor.execute(""" CREATE TABLE team_b (
        rally_id INTEGER PRIMARY KEY REFERENCES rallies(id),
        team_name TEXT,
        receiver INTEGER,
        digger INTEGER,
        hitter INTEGER
    );""")

    # rally table
    cursor.execute(""" CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    jersey_number INTEGER,
    team_name TEXT,
    total_hits INTEGER DEFAULT 0,
    total_passes INTEGER DEFAULT 0,
    total_digs INTEGER DEFAULT 0,
    total_blocks INTEGER DEFAULT 0,
    total_serves INTEGER DEFAULT 0,
    UNIQUE (jersey_number, team_name)
    )""")


def populate_rallies(cursor):
    cursor.execute("""
    INSERT INTO rallies (
        rally_id, team, round, winning_team, win_reason, lose_reason,
        receive_location, pass_land_location, hitter_location, hit_land_location,
        pass_rating, set_location, num_blockers, block_touch,
        serve_type, hit_type, digger_location
    )
    SELECT 
        rally, team, round, winning_team, win_reason, lose_reason,
        recieve_location, pass_land_location, hitter_location, hit_land_location,
        pass_rating, set_location, num_blockers, block_touch,
        serve_type, hit_type, digger_location
    FROM volleyball;
    """)


def populate_teamA(cursor):
    cursor.execute("""WITH numbered_volleyball AS (
        SELECT *, ROW_NUMBER() OVER () AS rn
        FROM volleyball
    ),
    numbered_rallies AS (
        SELECT *, ROW_NUMBER() OVER () AS rn
        FROM rallies
    )
    INSERT INTO team_a (rally_id, team_name, receiver, digger, hitter)
    SELECT r.id, v.team, v.recieve_location, v.digger_location, v.hitter_location
    FROM numbered_volleyball v
    JOIN numbered_rallies r ON v.rn = r.rn
    WHERE v.team = 'a';
    """)


def populate_teamB(cursor):
    cursor.execute("""WITH numbered_volleyball AS (
        SELECT *, ROW_NUMBER() OVER () AS rn
        FROM volleyball
    ),
    numbered_rallies AS (
        SELECT *, ROW_NUMBER() OVER () AS rn
        FROM rallies
    )
    INSERT INTO team_b (rally_id, team_name, receiver, digger, hitter)
    SELECT r.id, v.team, v.recieve_location, v.digger_location, v.hitter_location
    FROM numbered_volleyball v
    JOIN numbered_rallies r ON v.rn = r.rn
    WHERE v.team = 'b';
        """)


def populate_players(cursor):
    cursor.execute("""INSERT INTO players (jersey_number, team_name)
        SELECT DISTINCT recieve_location AS jersey_number, team
        FROM volleyball
        WHERE recieve_location IS NOT NULL
        UNION
        SELECT DISTINCT digger_location AS jersey_number, team
        FROM volleyball
        WHERE digger_location IS NOT NULL
        UNION
        SELECT DISTINCT hitter_location AS jersey_number, team
        FROM volleyball
        WHERE hitter_location IS NOT NULL;
        """)


    