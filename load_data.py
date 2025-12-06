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
    cursor.execute("DROP TABLE IF EXISTS teamA")
    cursor.execute("DROP TABLE IF EXISTS teamB")
    cursor.execute("DROP TABLE IF EXISTS players")

    # rally table
    cursor.execute(""" CREATE TABLE rallies (
    rally_id INTEGER PRIMARY KEY,
    team TEXT,
    round INTEGER,
    winning_team TEXT,
    win_reason TEXT,
    lose_reason TEXT,
    pass_location INTEGER,
    pass_land_location INTEGER,
    hit_location INTEGER,
    hit_land_location INTEGER,
    pass_rating TEXT,
    set_location TEXT,
    num_blockers INTEGER,
    block_touch TEXT,
    serve_type TEXT,
    hit_type TEXT,
    digger_location INTEGER,
    hitter_location INTEGER
    )""")

    # team A table

    # team B table

    # rally table


    