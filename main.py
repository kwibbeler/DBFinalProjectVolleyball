# this file will run the main functionality of the program
# it will load in the data file, create the derived tables,
# clean the data, and produce meaningful visualizations

import getpass
import pg8000

import load_data
import clean
import visualize



def setup():
    login = input('Login username: ')
    secret = getpass.getpass()

    credentials = {'user'    : login,
                'password': secret, 
                'database': 'csci403',
                'host'    : 'ada.mines.edu'}

    db = pg8000.connect(**credentials)

     
    return db.cursor()


if __name__ == "__main__":
    cursor = setup()