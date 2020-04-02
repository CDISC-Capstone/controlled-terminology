from flask import Flask, render_template, request, redirect, url_for, session, flash
import query
import sqlite3 as sql
import urllib
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html
import requests
import sys

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

@app.route('/')
def home():

    codes, terms = query.get_basic_data()
    #CL_activeDates, CL_current, CL_changes = query.get_codelist_changes(code, startDate, endDate)
    #term_activeDates, term_current, term_changes = query.get_term_changes(code, startDate, endDate)


    return render_template('homepage.html', url=host)



if __name__ == '__main__':
    app.run()
