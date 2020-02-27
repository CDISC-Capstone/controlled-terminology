import sqlite3 as sql
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


def create_tables():
    conn = sql.connect('CDISC.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS Code('
              'Code TEXT,'
              'Term_Type TEXT,'
              'Creation_Date TEXT,'
              'Deprecation_Date TEXT,'
              'PRIMARY KEY (Code));')

    c.execute('CREATE TABLE IF NOT EXISTS Codelist('
              'Code TEXT,'
              'Extensible TEXT,'
              'Name TEXT,'
              'Submission_Value TEXT,'
              'Synonyms TEXT,'
              'Definition TEXT,'
              'NCI_Preferred_Term TEXT,'
              'PRIMARY KEY (Code));')

    c.execute('CREATE TABLE IF NOT EXISTS Term('
              'Codelist TEXT,'
              'Code TEXT,'
              'Name TEXT,'
              'Submission_Value TEXT,'
              'Synonyms TEXT,'
              'Definition TEXT,'
              'NCI_Preferred_Term TEXT,'
              'PRIMARY KEY (Codelist, Code)'
              'FOREIGN KEY (Codelist) REFERENCES Codelist (Code));')

    c.execute('CREATE TABLE IF NOT EXISTS Changes('
              'Date TEXT,'
              'Code TEXT,'
              'Request_Code TEXT,'
              'Change_Type TEXT,'
              'Severity TEXT,'
              'Change_Summary TEXT,'
              'Original TEXT,'
              'New TEXT,'
              'Change_Instructions TEXT,'
              'PRIMARY KEY (Date, Code)'
              'FOREIGN KEY (Code) REFERENCES Code (Code));')


def read_data(filePath):
    # TODO: 1. Read in data, split according to table schema
    #       2. Add data to tables only if data is new
    print(filePath)
    data = pd.read_csv(filePath, sep='\t')
    return(data)


def read_changes(filePath):
    # TODO: 1. Read in data
    #       2. Determine severity of changes
    #       3. Change data to code table if update only
    #       4. Insert data into changelog table
    pass


# Debugging/Testing section
if __name__ == "__main__":
    # Reference variables
    firstPackageDate = "2014-10-06"
    archiveLink = "https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/"

    # Extracts archive HTML for BeautifulSoup
    archiveHTML = requests.get(archiveLink).text
    soup = BeautifulSoup(archiveHTML, 'html.parser')

    SDTMPackages = []
    SDTMChanges = []
    # Finds all SDTM links
    for link in soup.find_all('a'):
        # Finds all link references and tests if they are SDTM in .txt format
        end = link.get('href')
        SDTM = re.match(r"^SDTM%20Terminology\S*.txt$", end)

        # If it is a SDTM .txt link, split between package and changelist
        if SDTM:
            fullURL = archiveLink + end
            # Uses "Change" instead of "Changes" because of a typo in the link for 2016-09-30 changelist
            change = re.search("Change", end)

            if change:
                SDTMChanges.append(fullURL)
            else:
                SDTMPackages.append(fullURL)

    # Filter out packages/changelists that are before firstPackageDate (initially 2014 Q3)
    # This also extracts the date from the url to be used for sorting and to be used in the database
    SDTMPackages = [[i.split("%20")[-1][:-4], i] for i in SDTMPackages if i.split("%20")[-1][:-4] >= firstPackageDate]
    SDTMChanges = [[i.split("%20")[-1][:-4], i] for i in SDTMChanges if i.split("%20")[-1][:-4] >= firstPackageDate]

    # Sorts by extracted date mostly for the typo noted above, but helps ensure packages are read in chronologically
    SDTMPackages.sort()
    SDTMChanges.sort()

    # data = read_data(path)
    # Codelists = data[data["Codelist Code"].isna()]
    # Terms = data[data["Codelist Code"].notna()]
