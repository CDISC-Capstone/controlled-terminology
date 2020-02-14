from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sys

app = Flask(__name__)


@app.route('/')
def home():
    a = 1
    b = 2
    c = a + b
    return render_template('homepage.html', c=c)


if __name__ == '__main__':
    app.run()
