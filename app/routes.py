from app import app
from app.models import WciaContent
from bs4 import BeautifulSoup
from flask import Flask, request
import requests
import pdb
from dotenv import load_dotenv
load_dotenv()

@app.route('/')
@app.route('/index')
def index():
    return "hello world"
@app.route('/wcia')
def wcia():
    URL = 'https://www.wcia.com/news/local-news/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    articles = soup.find_all("a", class_="article-list__gradient-link")
    article_links = list(set(filter(None, [link.get('href') for link in articles])))
    article_links = list(filter(lambda link: link and 'https://www.wcia.com/ciliving-tv' not in link, article_links))

    print(article_links[0:1])
    print(article_links[0])
    print(len(article_links))
    for url in article_links[0:1]:
        article_page = requests.get(url)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')
        time = ':'.join(article_soup.find(class_="article-meta").contents[-2].text.split(":")[1:3]).strip()
        # time = 'Jun 14, 2023 / 03:35 PM CDT'
        all_body = article_soup.find(class_="article-content article-body rich-text")
        text = all_body.get_text(strip=True)
        breakpoint()

    print('uh oh')
    return str(soup.prettify())