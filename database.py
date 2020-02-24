import sqlite3 as sql
import pandas as pd

def createTables():
    conn = sql.connect('CDISC.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS Code('
              'Code TEXT,'
              'Term_Type TEXT,'
              'Creation_Date TEXT,'
              'Deprecated_Date TEXT,'
              'PRIMARY KEY (Code))')

    c.execute('CREATE TABLE IF NOT EXISTS Codelist('
              'Code TEXT,'
              'Extensible TEXT,'
              'Name TEXT,'
              'Submission_Value TEXT,'
              'Synonyms TEXT,'
              'Definition TEXT,'
              'NCI_Preferred_Term TEXT,'
              'PRIMARY KEY (Code))')

    c.execute('CREATE TABLE IF NOT EXISTS Term('
              'Codelist TEXT,'
              'Code TEXT,'
              'Name TEXT,'
              'Submission_Value TEXT,'
              'Synonyms TEXT,'
              'Definition TEXT,'
              'NCI_Preferred_Term TEXT,'
              'PRIMARY KEY (Codelist, Code)'
              'FOREIGN KEY (Codelist) REFERENCES Codelist (Code))')

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
              'FOREIGN KEY (Code) REFERENCES Code (Code))')

def readData():
    # TODO: 1. Read in data, split according to table schema
    #       2. Add data to tables only if data is new

    pass

def readChanges():
    # TODO: 1. Read in data
    #       2. Determine severity of changes
    #       3. Change data to code table if update only
    #       4. Insert data into changelog table

    pass