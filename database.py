import sqlite3 as sql
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


# Creates tables in the database
def create_tables():
    conn = sql.connect('CDISC.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS Code('
              'Code TEXT,'
              'Term_Type TEXT,'
              'Standard TEXT,'
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
              'PRIMARY KEY (Code),'
              'FOREIGN KEY (Code) REFERENCES Code (Code));')

    c.execute('CREATE TABLE IF NOT EXISTS Term('
              'Codelist TEXT,'
              'Code TEXT,'
              'Submission_Value TEXT,'
              'Synonyms TEXT,'
              'Definition TEXT,'
              'NCI_Preferred_Term TEXT,'
              'PRIMARY KEY (Codelist, Code),'
              'FOREIGN KEY (Code) REFERENCES Code (Code),'
              'FOREIGN KEY (Codelist) REFERENCES Codelist (Code));')

    c.execute('CREATE TABLE IF NOT EXISTS Changes('
              'Date TEXT,'
              'Code TEXT,'
              'Codelist TEXT,'
              'Term_Type TEXT,'
              'Request_Code TEXT,'
              'Change_Type TEXT,'
              'Severity TEXT,'
              'Change_Summary TEXT,'
              'Original TEXT,'
              'New TEXT,'
              'Change_Instructions TEXT,'
              'PRIMARY KEY (Date, Code, Codelist, Request_Code, Term_Type, Original, New),'
              'FOREIGN KEY (Code) REFERENCES Code (Code));')

    conn.close()


# Adds the codelists/terms into the database
def read_data(date, filePath, standard):
    connection = sql.connect('CDISC.db')
    data = pd.read_csv(filePath, sep='\t', engine='python')

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
            connection.execute('INSERT INTO Code(Code, Term_Type, Standard, Creation_Date, Current_Version, Deprecation_Date)'
                               'VALUES (?, ?, ?, ?, ?, ?);', (code, "CDISC Codelist", standard, date, date, None))

            # Insert into Codelist table if not already in table
            connection.execute('INSERT INTO Codelist(Code, Extensible, Name, Submission_Value, Synonyms, Definition, NCI_Preferred_Term)'
                               'VALUES (?, ?, ?, ?, ?, ?, ?);', (code, extensible, name, value, synonyms, definition, nci))
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
        value = str(row['CDISC Submission Value'])
        synonyms = str(row['CDISC Synonym(s)'])
        definition = row['CDISC Definition']
        nci = row['NCI Preferred Term']

        # Inserts term into Code table
        try:
            # Insert into Code table if not already in table
            connection.execute('INSERT INTO Code(Code, Term_Type, Standard, Creation_Date, Current_Version, Deprecation_Date)'
                               'VALUES (?, ?, ?, ?, ?, ?);', (code, "Term", standard, date, date, None))
        # If term is already in Code (throws error), update tables as necessary
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

        # Insert term into Term table
        try:
            # Attempt to insert into Term table (successful if not already in it)
            connection.execute(
                'INSERT INTO Term(Codelist, Code, Submission_Value, Synonyms, Definition, NCI_Preferred_Term)'
                'VALUES (?, ?, ?, ?, ?, ?);', (codelistCode, code, value, synonyms, definition, nci))
        # If this raises an error, then update what's in the table
        except sql.IntegrityError:
            # Update term values with current version, even if nothing has changed
            connection.execute('UPDATE Term '
                               'SET Submission_Value = ?, Synonyms = ?, Definition = ?, NCI_Preferred_Term = ? '
                               'WHERE Codelist = ? AND Code = ?;', (value, synonyms, definition, nci, codelistCode, code))
        connection.commit()

    connection.close()


# Adds the changes into the database
def read_changes(date, filePath, standard):
    connection = sql.connect('CDISC.db')
    data = pd.read_csv(filePath, sep='\t', engine='python')

    # Explicitly enforce foreign key constraint as this is FALSE by default
    # This is for terms that may be removed with the first changelist and so do not exist in Code table
    connection.execute('PRAGMA foreign_keys = TRUE;')

    # Add changes to table
    for i, row in data.iterrows():
        reqCode = row['Request Code']
        termType = row['CDISC Term Type']
        codelistShort = row['CDISC Codelist (Short Name)']
        changeType = row['Change Type']
        code = row['NCI Code']
        summary = row['Change Summary']
        original = str(row['Original'])
        new = str(row['New'])

        # Older changelists do not have change instruction column so have 10 columns total
        # If there are change instructions (11 columns), extract it
        if len(data.columns) == 11:
            instructions = row['Change Implementation Instructions']
        # Otherwise set as None
        else:
            instructions = None

        # Determine severity of change - This is subjective and may be changed as necessary
        # Addition is moderate as it may not affect anything
        if changeType == "Add":
            severity = "Moderate"
        # Removal is major as it may have big effects
        elif changeType == "Remove":
            severity = "Major"
        # If update, look into what exactly changed
        elif changeType == "Update":
            if "Synonym" in summary:
                severity = "Minor"
            elif "Codelist Name" in summary:
                severity = "Moderate"
            elif "Definition" in summary or "Submission Value" in summary:
                severity = "Major"
            elif "NCI Preferred Term" in summary:
                severity = "Moderate"
        else:
            severity = "Undetermined"

        # If code is not in Code table, this will throw an error since it is a foreign key in Changes
        try:
            connection.execute('INSERT INTO Changes(Date, Code, Codelist, Term_Type, Request_Code, Change_Type, Severity, Change_Summary, Original, New, Change_Instructions)'
                               'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (date, code, codelistShort, termType, reqCode, changeType, severity, summary, original, new, instructions))

            # If a term has been removed, note that in Code
            if changeType == "Remove":
                connection.execute('UPDATE Code '
                                   'SET Current_Version = ?,'
                                   '    Deprecation_Date = ? '
                                   'WHERE Code = ?;', (date, date, code))

        # If a foreign key constraint has failed, add that code to Code table and then insert
        except sql.IntegrityError:
            # If it is a removed term, termType will be "Term"
            # If it is a removed codelist, termType will be "CDISC Codelist"
            connection.execute('INSERT INTO Code(Code, Term_Type, Standard, Creation_Date, Current_Version, Deprecation_Date)'
                               'VALUES(?, ?, ?, ?, ?, ?);', (code, termType, standard, date, date, date))

            connection.execute('INSERT INTO Changes(Date, Code, Codelist, Term_Type, Request_Code, Change_Type, Severity, Change_Summary, Original, New, Change_Instructions)'
                               'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (date, code, codelistShort, termType, reqCode, changeType, severity, summary, original, new, instructions))
        connection.commit()

    connection.close()


# This function gets all package and changelist urls for a given standard
def get_packages(firstPackageDate, standard):
    # Determine archive link based on standard
    if (standard == "SDTM") or (standard == "CDASH"):
        archiveLink = "https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/"
    else:
        archiveLink = ""

    # Extracts archive HTML for BeautifulSoup
    archiveHTML = requests.get(archiveLink).text
    soup = BeautifulSoup(archiveHTML, 'html.parser')

    packages = []
    changes = []
    # Finds all links for that standard
    for link in soup.find_all('a'):
        # Finds all link references and tests if they are of that format in .txt format
        end = link.get('href')
        txt = re.match(r"^{}%20Terminology\S*.txt$".format(standard), end)

        # If it is a SDTM .txt link, split between package and changelist
        if txt:
            fullURL = archiveLink + end
            # Uses "Change" instead of "Changes" because of a typo in the link for 2016-09-30 SDTM changelist
            if "Change" in end:
                changes.append(fullURL)
            else:
                packages.append(fullURL)

    # Filter out packages/changelists that are before firstPackageDate (initially 2014 Q3)
    # This also extracts the date from the url to be used for sorting and to be used in the database
    # Final form is list with elements in format [date, link]
    packages = [[i.split("%20")[-1][:-4][0:10], i] for i in packages if i.split("%20")[-1][:-4] >= firstPackageDate]
    changes = [[i.split("%20")[-1][:-4][0:10], i] for i in changes if i.split("%20")[-1][:-4] >= firstPackageDate]

    # Sorts by extracted date mostly for the typo noted above, but helps ensure packages are read in chronologically
    packages.sort()
    changes.sort()

    return packages, changes


# Loads the initial data for a given standard (default SDTM from 2014 Q3 - ~2019Q4)
# Because of how it is coded, it will look for every package up to present from firstPackageDate
# It will take a long time, especially as more packages are added as it has at least O(n) complexity,
# n being the number of terms, codelists, and changes for every package combined
def initial_load(firstPackageDate = "2014-10-06", standard="SDTM"):
    packages, changes = get_packages(firstPackageDate, standard)

    for i in packages:
        read_data(i[0], i[1], standard)
        print(i[0], "package loaded")
    print("Packages loaded")

    for i in changes:
        read_changes(i[0], i[1], standard)
        print(i[0], "changes loaded")
    print("Changelists loaded")


# Automatically updates the database with all recent packages/changelogs not in the database for a given standard
# Assumes that there is at least one package in the database of that standard
def update_database(standard):
    connection = sql.connect('CDISC.db')

    # Get the latest version date in the database
    latestVersion = connection.execute('SELECT Current_Version '
                                       'FROM Code '
                                       'WHERE Standard = ? '
                                       'ORDER BY Current_Version DESC '
                                       'LIMIT 1;', (standard,)).fetchall()[0][0]

    packages, changes = get_packages(latestVersion, standard)

    # Remove first element as that is already in the database
    packages = packages[1:]
    changes = changes[1:]

    # If there are new packages, read into database
    if len(packages) > 0:
        for i in packages:
            read_data(i[0], i[1], standard)
            print(i[0], "package loaded")
        print("Packages updated")

        for i in changes:
            read_changes(i[0], i[1], standard)
            print(i[0], "changes loaded")
        print("Changelists updated")
    # Otherwise, nothing to upload
    else:
        print("Database is up to date")


# Use this function to manually upload packages and changelogs from the same release
# This is meant for older packages after they have been cleaned since newer ones can be updated automatically,
# but newer packages should be able to be uploaded here too
# package and changelog are file paths to a tab delimited .txt file containing the required columns format and names
def manual_load_data(date, package, changelog, standard):
    read_data(date, package, standard)
    print(date, "package uploaded")
    read_changes(date, changelog)
    print(date, "changelog uploaded")


# Debugging/Testing section
if __name__ == "__main__":
    data = pd.read_csv(r"C:\Users\voidt\Downloads\SDTM Terminology Changes 2019-12-20.txt", sep='\t')
    orig = data[data["Original"].isna()][["NCI Code", "Original", "New"]]

    for i, row in orig.iterrows():
        print(row["Original"])