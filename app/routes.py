from app import app
from app.wcia_web_scraper import wcia
from bs4 import BeautifulSoup
from flask import Flask, request
# import pdb
from dotenv import load_dotenv
from datetime import datetime, timedelta


@app.route('/')
@app.route('/index')
def index():
    return "hello world"
@app.route('/wcia')
def wcia_route():
    return wcia()
