from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sys

app = Flask(__name__)


@app.route('/')
def home():
    a = 5
    b = 2
    c = a + b
    var = c + a + 2
    return render_template('homepage.html', c=c, var=var)


if __name__ == '__main__':
    app.run()
