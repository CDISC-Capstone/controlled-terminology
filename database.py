import sqlite3 as sql
import pandas as pd


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
    # This uses the ugly %20 for spaces in the url. This could be cleaned up/automated later
    path = "https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/SDTM%20Terminology%202014-10-06.txt"
    data = read_data(path)
    Codelists = data[data["Codelist Code"].isna()]
    Terms = data[data["Codelist Code"].notna()]
    print(Codelists)
    print(Terms)
