from flask import Flask, request
from bs4 import BeautifulSoup
import requests

class WciaContent():
    URL = 'https://www.wcia.com/news/local-news/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')