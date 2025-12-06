# this file will run the main functionality of the program
# it will load in the data file, create the derived tables,
# clean the data, and produce meaningful visualizations

import pg8000

import load_data
import clean
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

    # create the dervived tables

    # clean the data

    # create visualizations
