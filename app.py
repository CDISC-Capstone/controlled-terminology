from flask import Flask, render_template, request, redirect, url_for, session, flash
import query
from datetime import datetime
import time
import sqlite3 as sql
import urllib
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html
import requests
import sys

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    codes: [(Code, Term Type, Standard, Submission Value, Name)]
    terms: [(Code, Term Type, Standard, Submission Value)]
    '''
    codes, terms = query.get_basic_data()
    list_of_codes = [code[0] for code in codes]
    list_of_terms = [term[0] for term in terms]

    if request.method == 'POST':
        code = request.form['codes']
        term = request.form['terms']
        startDate = request.form['start_date']
        startDate = datetime.strptime(startDate, '%B %d, %Y').strftime('%Y-%d-%m')
        endDate = request.form['end_date']
        endDate = datetime.strptime(endDate, '%B %d, %Y').strftime('%Y-%d-%m')

        '''
        CL_activeDates: [Creation Date, Deprecation Date]
        CL_current: [Code, Extensible?, Name, Submission Value, Synonyms, Definition, NCI Preferred Term]
        CL_changes: [Date, Code, Codelist, Term Type, Request Code, Change Type, Severity, Change Summary, Original, New,
                    Change Instructions]
        '''
        CL_activeDates, CL_current, CL_changes = query.get_codelist_changes(code, startDate, endDate)

        '''
        term_activeDates: [Creation Date, Deprecation Date]
        term_current: [Codelist, Code, Submission Value, Synonyms, Definition, NCI Preferred Term]
        term_changes: [Date, Code, Codelist, Term Type, Request Code, Change Type, Severity, Change Summary, Original, New,
                    Change Instructions]
        '''
        term_activeDates, term_current, term_changes = query.get_term_changes(term, startDate, endDate)

        print(code, term)
        print(CL_activeDates)
        print(CL_current)
        print(CL_changes)

        print(term_activeDates)
        print(term_current)
        print(term_changes)

    #print(codes)
    #print(terms)
    #print(list_of_codes)

    return render_template('homepage.html', url=host, list_of_codes=list_of_codes, list_of_terms=list_of_terms)



if __name__ == '__main__':
    app.run()
