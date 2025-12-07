# this file will run the main functionality of the program
# it will load in the data file, create the derived tables,
# clean the data, and produce meaningful visualizations

import pg8000

import load_data
import clean_data
import visualize



def setup():
    login = input('Login username: ')
    secret = input('Password: ')

    credentials = {'user'    : login,
                'password': secret, 
                'database': 'csci403',
                'host'    : 'ada.mines.edu'}

    return pg8000.connect(**credentials)

     
    


if __name__ == "__main__":
    # establish the connection to the database 
    connection = setup()
    cursor = connection.cursor()

    # create the table and bulk load the data
    load_data.create_table(cursor)
    load_data.bulk_load_csv(connection)
    connection.commit()

    # clean the data
    clean_data.replace_empty_strings(cursor)
    clean_data.standardize_columns(cursor)
    connection.commit()

    # create the dervived tables
    load_data.create_derived_tables(cursor)
    # make sure to not create duplicate entries in the tables
    cursor.execute("TRUNCATE rallies, team_a, team_b, players RESTART IDENTITY CASCADE;")
    load_data.populate_rallies(cursor)
    load_data.populate_teamA(cursor)
    load_data.populate_teamB(cursor)
    load_data.populate_players(cursor)
    connection.commit()
    print("created derived tables")

    # add aggregate columns to the tables 
    clean_data.player_aggregates(cursor)
    clean_data.team_aggregates(cursor)
    connection.commit()
    print("created aggregate player and team columns")

    # create visualizations
