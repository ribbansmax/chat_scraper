from app import app
from app.models import WciaContent
from bs4 import BeautifulSoup
from flask import Flask, request
import requests
import pdb

@app.route('/')
@app.route('/index')
def index():
    return "hello world"
@app.route('/wcia')
def wcia():
    URL = 'https://www.wcia.com/news/local-news/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    breakpoint()
    return str(soup.prettify())