from flask import Flask, render_template, request, redirect, url_for, session, flash
import database
import urllib
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from bokeh.embed import file_html
import requests
import sys

app = Flask(__name__)


@app.route('/')
def home():
    firstPackageDate = "2014-10-06"
    SDTM_packages, SDTM_changes = database.get_packages(firstPackageDate)

    link = SDTM_packages[0][1]  # https://evs.nci.nih.gov/ftp1/CDISC/SDTM/Archive/SDTM%20Terminology%202014-10-06.txt
    f = requests.get(link)

    header = f.text.split('\n')[0]
    case = []

    for line in f.text.split('\n'):
        for data in line.text.split('\t'):
            case.append(data)

    print(case, file=sys.stderr)

    plot = figure()
    plot.square([1, 2], [3, 4])
    file = file_html(plot, CDN, "test")
    show(plot)

    return render_template('homepage.html', SDTM_packages=SDTM_packages, SDTM_changes=SDTM_changes)



if __name__ == '__main__':
    app.run()
