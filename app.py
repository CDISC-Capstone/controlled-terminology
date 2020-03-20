from flask import Flask, render_template, request, redirect, url_for, session, flash
import database
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
    firstPackageDate = "2014-10-06"
    SDTM_packages, SDTM_changes = database.get_packages(firstPackageDate, 'SDTM')

    link = SDTM_packages[0][1]  # https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/SDTM%20Terminology%202014-10-06.txt
    f = requests.get(link)
    header = f.text.split('\n')[0].split("\t")

    case = []  # list type: contains each entry
    for i in range(1, len(SDTM_packages)):
        link = SDTM_packages[i][1]  # https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/SDTM%20Terminology%202014-10-06.txt
        f = requests.get(link)

        for line in f.text.split('\n'):
            for data in line.split('\t'):
                case.append(data)

    print(case, file=sys.stderr)

    return render_template('homepage.html', url=host, SDTM_packages=SDTM_packages, SDTM_changes=SDTM_changes)



if __name__ == '__main__':
    app.run()
