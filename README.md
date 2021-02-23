# NPI PHYSICIAN DATABASE PROJECT
## Aim: 
To design a simple interactive program that prompts the user to enter the number of physician's information required. 

## Description:
The program accepts integer value and doesn't require any API keys or OAuths. Upon entering non-integer values it prompts the user untill the acceptable value is entered. 

## Dataset and Libraries:
The program performs webscraping from https://www.abim.org/verify-physician.aspx?type=npi&npi= which is a search box. The search query is initiated upon entering the NPI numbers sequentially pulled from the directory NPI_April_data.csv. 

Libraries used:
BeautifulSoup, requests, json, pandas, csv, os, sqlite3, sys, plotly

## Usage:
Upon running the program successfully an output database file is created in the user's directory. 


