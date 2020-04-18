# CDISC Controlled Terminology Visualization Tool
This repository consists of files for a browser based visualization of the changes of CDISC controlled terminology (CT) codelists and terms for a selected time period. The codelist, term, and changes data are stored in a local sqlite database. There are 3 main python files: app.py, database.py, and query.py.

Currently, it only supports SDTM and CDASH standards, but can be expanded to other standards by editing the first if statement in `get_packages()` in database.py.

## app.py
app.py functions as the frontend of the project. **Note that it requires the local database be already be created**.

## database.py
database.py manages the database CDISC.db. To create the database, run `create_tables()` then `initial_load()`. This will create the 4 required tables and by default populate them with SDTM data from 2014-10-06 and later. The data is gathered from the appropriate .txt files in the NCI archive. The database may be updated automatically from the archive for a given standard using `update_database()` or manually from a file by using `manual_load_data()`.

### Important note on database.py
**Because `read_data()` assumes reading the same term code means another version of the term has been updated, some codelists are not inserted correctly, particularly sister codelists with test codes and test names (i.e. C100133 and C100134) with the first one in the file being written into the database. This results in one being empty (i.e. C100133 since codelist C100134 occurs first)**. This was unfortunately an oversight that went unnoticed. As far as it can be seen, this only concerns terms in particular and nothing else.

## query.py
query.py serves as the bridge between app.py and database.py to separate database management from querying it.
