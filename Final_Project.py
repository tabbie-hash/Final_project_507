from bs4 import BeautifulSoup
import requests                                                     
# c:\Users\tabas\OneDrive\Desktop\507Lab\Final_project_507
import json
import pandas as pd
import csv
import os
import sqlite3 as sqlite
from sqlite3 import Error
import sqlite3
import sys


filename = "NPI_April_data.csv"
baseurl = "https://www.abim.org/verify-physician.aspx?type=npi&npi="

def read_datasource(filename):
    '''Read a comma-separated values (csv) file into DataFrame on which python code can be implemented
    
    Parameters
    ----------
    filename: string
    
    Returns
    -------
    dataframe or textparser - a two-dimensional data structure with labeled axes.
    '''
    data_source = pd.read_csv(filename, delimiter=",")
    return data_source


def fetch_input_list(dataframe, inp_num):
    '''Takes a python readable dataframe and extracts desired values from the desired column and presents it in a list format.
    
    Parameters
    ----------
    dataframe = python readable table
    
    Returns
    -------
    list
    '''
    input_column_intermediate = dataframe.NPI.drop_duplicates().to_frame()
    input_column = input_column_intermediate.NPI[:inp_num]
    npi_list = []
    for npi in input_column:
        npi_list.append(npi)
    return npi_list


def collect_data(url, npi_id, cache={}):
    '''Requests url using the existing cache
    
    Parameters
    ----------
    url - string
    npi_id - integer
    cache - dictionary
    
    Returns
    -------
    cache
    '''  
    npi_id = str(npi_id)
    if npi_id in cache: 
        print("Using cache....") 

    else:
        print("Fetching.....")  
        response = requests.get(url)
        parse = BeautifulSoup(response.text, 'html.parser')

        phy_name = collect_names(parse)
        phy_detail = collect_details(parse)

        cache[npi_id] = (phy_name, phy_detail)


    return cache

def collect_names(parse):
    '''Returns the names of the physicians for a particular NPI ID
    
    Parameters
    ----------
    parse - string

    Returns
    -------
    physician_name - string
    '''

    physician_name_divs = parse.find('h1', id="page-title")
    for physician_name in physician_name_divs:
        if physician_name[0:6] == 'Search':
            return "NO PHYSICIAN"
        else:
            return physician_name


def collect_details(parse):
    '''Returns the details of the physicians for a particular NPI ID
    
    Parameters
    ----------
    parse - string

    Returns
    -------
    physician_details - string
    '''

    search_div = parse.find(id="article")
    physician_detail_divs = search_div.find_all('div', class_='abim_voc-profile')

    if physician_detail_divs == []:
        return "NO PHYSICIAN DETAILS"
    else:
        for detail in physician_detail_divs:
            physician_details = detail.text
            return physician_details


def create_table(phy):
    '''Creates the table in the database.
    
    Parameters
    ----------
    phy - connection handle to the database
    
    Returns
    -------
    None
    '''
    a = phy.cursor()

    sql_command = '''CREATE TABLE ALL_PHY_DB (NPI_ID INT, PHYSICIAN_NAME VARCHAR(50), PHYSICIAN_DETAILS VARCHAR(300));'''
    a.execute(sql_command)

    phy.commit()
        

def table_insert(phy, table_data):
    '''Inserts the data collected into the columns of the table created in database file.
    
    Parameters
    ----------
    phy - connection handle to database 
    table_data - tuple
    
    Returns
    -------
    None
    '''
    a = phy.cursor()
    
    sql_insert_query = '''INSERT INTO ALL_PHY_DB (NPI_ID , PHYSICIAN_NAME, PHYSICIAN_DETAILS) VALUES (?,?,?)'''
    a.executemany(sql_insert_query, table_data)
    
    phy.commit()

       

def file_convertor(db_file):
    '''Converts database file to into csv file
    
    Parameters
    ----------
    db_file - database file
    
    Returns
    -------
    csv file
    '''
    conn = sqlite.connect(db_file, isolation_level=None,detect_types=sqlite.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM ALL_PHY_DB ", conn)
    db_df_final = db_df.to_csv('physiciandatabase.csv', index=False)
    return db_df_final


def load_cache(): 
    '''Read the cache file and check the contents 
    
    Parameters
    ----------
    None
        
    
    Returns
    -------
    cache
    '''
    try:
        cache_file = open("cache.json", 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache): 
    '''Writes on the cache file to add new urls.
    
    Parameters
    ----------
    cache - dictionary
    
    Returns
    -------
    None
    '''
    cache_file = open('cache.json', 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()



if __name__ == "__main__":
    while True:
        user_input = input('Please enter the a number between 1-200 to specify the number of NPI IDs you wish to select or type "end" to end:')
        if user_input.isnumeric():
            user_input = int(user_input)
            if user_input in list(range(1,201)):
                print("Collecting your data........")
                dbfile = 'physiciandatabase.db'
                cache = load_cache()
                dataframe = read_datasource(filename)
                input_npi_list = fetch_input_list(dataframe, user_input)
                table_data = []
                for one_npi in input_npi_list:
                    cache = collect_data(baseurl,one_npi,cache)
                    save_cache(cache)
                    
                    phy_name = cache[str(one_npi)][0]
                    phy_detail = cache[str(one_npi)][1]
                    table_tuple = (one_npi, phy_name, phy_detail)
                    table_data.append(table_tuple)

                phy = sqlite.connect('physiciandatabase.db') 
                create_table(phy)
                table_insert(phy, table_data)
                file_convertor(dbfile)
                csv_out = 'physiciandatabase.csv'
                output = read_datasource(csv_out)
                print(output)

                print("\n*************************************************************************\n")
                print("YOU MAY ALSO OPEN THE FILE 'physiciandatabase.csv' FROM YOUR DIRECTORY!\nPLEASE ADJUST ROW/COLUMN HEIGHTS AND TEXT ALIGNMENT!\nALSO NOTE THAT THERE IS ALSO A '.db' FILE FOR YOU!\n*-*-*-*THANK YOU*-*-*")
                print("\n*************************************************************************\n")
                sys.exit()
            elif user_input not in list(range(1,201)):
                print('Oops!The number of requested NPI IDs are out of range!!\nPlease enter the a number between 1-200 to specify the number of NPI IDs you wish to select or type "end" to end:')
            else:
                print('!!SYSTEM ERROR!!\nPLEASE TYPE CORRECTLY')
        elif user_input.isalpha():
            if user_input in ['end', 'End', 'END']:
                sys.exit()
            elif user_input not in ['exit', 'Exit', 'EXIT']:
                print("Do you wish to end? If yes, then type end.")
            else:
                print("'!!SYSTEM ERROR!!\nPLEASE TYPE CORRECTLY'")
        else:
            print("'!!SYSTEM ERROR!!\nPLEASE TYPE CORRECTLY'")
    
        