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
              'Current_Version TEXT,'
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


def read_data(date, filePath):
    connection = sql.connect('CDISC.db')
    data = pd.read_csv(filePath, sep='\t')

    # Codelists have "Codelist Code" as NA as Code gives that code
    codelists = data[data['Codelist Code'].isna()]
    terms = data[data['Codelist Code'].notna()]

    # Insert codelists into database
    for i, row in codelists.iterrows():
        code = row['Code']
        extensible = row['Codelist Extensible (Yes/No)']
        name = row['Codelist Name']
        value = row['CDISC Submission Value']
        synonyms = row['CDISC Synonym(s)']
        definition = row['CDISC Definition']
        nci = row['NCI Preferred Term']

        # Inserts codelist into table
        try:
            # Insert into Code table if not already in table
            connection.execute('INSERT INTO Code(Code, Term_Type, Creation_Date, Current_Version, Deprecation_Date)'
                               'VALUES (?, ?, ?, ?, ?);', (code, "codelist", date, date, None))

            # TODO: Check changelist to see if codelist has been depreciated (for older codelists added later)

            # Insert into Codelist table if not already in table
            connection.execute('INSERT INTO Codelist(Code, Extensible, Name, Submission_Value, Synonyms, Definition, NCI_Preferred_Term)'
                               'VALUES (?, ?, ?, ?, ?, ?, ?);', (code, extensible, name, value, synonyms, definition, nci))
            connection.commit()
        # If codelist is already in tables (throws error), update tables as necessary
        except sql.IntegrityError:
            # Get version date of what's in the database
            versionDate = connection.execute('SELECT Current_Version '
                                             'FROM Code '
                                             'WHERE Code = ?;', (code,)).fetchall()[0][0]

            # If older package than what's currently on file, do not modify what's in the codelist table
            if date < versionDate:
                # The code has existed before what's in code table, update the creation date
                connection.execute('UPDATE Code '
                                   'SET Creation_Date = ? '
                                   'WHERE Code = ?', (date, code))
            # If newer package, update the code and codelist tables
            else:
                # Set this package's date as current version
                connection.execute('UPDATE Code '
                                   'SET Current_Version = ? '
                                   'WHERE Code = ?', (date, code))

                # Update codelist values with current version, even if nothing has changed
                connection.execute('UPDATE Codelist '
                                   'SET Extensible = ?, Name = ?, Submission_Value = ?, Synonyms = ?, Definition = ?, NCI_Preferred_Term = ? '
                                   'WHERE Code = ?;', (extensible, name, value, synonyms, definition, nci, code))
            connection.commit()

    # Insert terms into database
    for i, row in terms.iterrows():
        code = row['Code']
        codelistCode = row['Codelist Code']
        value = row['CDISC Submission Value']
        synonyms = row['CDISC Synonym(s)']
        definition = row['CDISC Definition']
        nci = row['NCI Preferred Term']

        # Inserts term into table
        try:
            # Insert into Code table if not already in table
            connection.execute('INSERT INTO Code(Code, Term_Type, Creation_Date, Current_Version, Deprecation_Date)'
                               'VALUES (?, ?, ?, ?, ?);', (code, "term", date, date, None))

            # TODO: Check changelist to see if term has been depreciated (for older terms added later)

            # Insert into Term table if not already in table
            connection.execute('INSERT INTO Term(Codelist, Code, Submission_Value, Synonyms, Definition, NCI_Preferred_Term)'
                               'VALUES (?, ?, ?, ?, ?, ?);', (codelistCode, code, value, synonyms, definition, nci))
            connection.commit()
        # If term is already in tables (throws error), update tables as necessary
        except sql.IntegrityError:
            # Get version date of what's in the database
            versionDate = connection.execute('SELECT Current_Version '
                                             'FROM Code '
                                             'WHERE Code = ?;', (code,)).fetchall()[0][0]

            # If older package than what's currently on file, do not modify what's in the term table
            if date < versionDate:
                # The code has existed before what's in code table, update the creation date
                connection.execute('UPDATE Code '
                                   'SET Creation_Date = ? '
                                   'WHERE Code = ?', (date, code))
            # If newer package, update the code and term tables
            else:
                # Set this package's date as current version
                connection.execute('UPDATE Code '
                                   'SET Current_Version = ? '
                                   'WHERE Code = ?', (date, code))

                # Update term values with current version, even if nothing has changed
                connection.execute('UPDATE Term '
                                   'SET Submission_Value = ?, Synonyms = ?, Definition = ?, NCI_Preferred_Term = ? '
                                   'WHERE Codelist = ? AND Code = ?;', ( value, synonyms, definition, nci, codelistCode, code))
            connection.commit()

    connection.close()


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
    # Final form is list with elements in format [date, link]
    SDTMPackages = [[i.split("%20")[-1][:-4][0:10], i] for i in SDTMPackages if i.split("%20")[-1][:-4] >= firstPackageDate]
    SDTMChanges = [[i.split("%20")[-1][:-4][0:10], i] for i in SDTMChanges if i.split("%20")[-1][:-4] >= firstPackageDate]

    # Sorts by extracted date mostly for the typo noted above, but helps ensure packages are read in chronologically
    SDTMPackages.sort()
    SDTMChanges.sort()

    read_data(SDTMPackages[0][0], SDTMPackages[0][1])
