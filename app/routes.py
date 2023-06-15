from app import app
from app.models import WciaContent
from bs4 import BeautifulSoup
from flask import Flask, request
import requests
import pdb
from dotenv import load_dotenv
load_dotenv()
import os
import openai
from datetime import datetime, timedelta


api_key = os.getenv("API_KEY")
model = "gpt-3.5-turbo"

@app.route('/')
@app.route('/index')
def index():
    return "hello world"
@app.route('/wcia')
def wcia():
    current_time = datetime.now()
    time_threshold = current_time - timedelta(hours=24)

    URL = 'https://www.wcia.com/news/local-news/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    articles = soup.find_all("a", class_="article-list__gradient-link")
    article_links = list(set(filter(None, [link.get('href') for link in articles])))
    article_links = list(filter(lambda link: link and 'https://www.wcia.com/ciliving-tv' not in link, article_links))

    print(article_links[0:1])
    print(article_links[0])
    print(len(article_links))

    article_texts = {}
    for url in article_links:
        article_page = requests.get(url)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')
        # time = ':'.join(article_soup.find(class_="article-meta").contents[-2].text.split(":")[1:3]).strip()
        # time = 'Jun 14, 2023 / 03:35 PM CDT'
        update_time_str = article_soup.find(class_="article-meta").contents[-2].text.strip()
        update_time_str = update_time_str.replace('Updated: ', '')  # Remove the 'Updated: ' prefix
        update_time_str = update_time_str[:-4]  # Remove the trailing ' PM' or ' AM'
        update_time = datetime.strptime(update_time_str, "%b %d, %Y / %I:%M %p")



        if update_time >= time_threshold:
            all_body = article_soup.find(class_="article-content article-body rich-text")
            text = all_body.get_text(strip=True)

            if True:
                openai.api_key = os.getenv("API_KEY")

                completion = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Summarize the following messages succinctly if they would be interesting to a local with no children. Weather is interesting, but keep it short. Crime, local sports, and school news except UIUC is not interesting. Respond excatly with 'Not interesting.' if the news is not interesting"},
                    {"role": "user", "content": text}
                ]
                )
                response = completion.choices[0].message

                if response["role"] == "assistant":
                    assistant_content = response["content"]
                    if assistant_content != 'Not interesting.':
                        article_texts[url] = assistant_content
                    else:
                        article_texts[url] = 'Not interesting.'
            print(completion.choices[0].message)
        # breakpoint()

    print('uh oh')
    response_string = ""
    for url, summary in article_texts.items():
        response_string += f"<p><a href='{url}'>{summary}</a></p>"

    html_template = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f5f5f5;
                    padding: 20px;
                }}
                p {{
                    margin-bottom: 10px;
                }}
                a {{
                    color: #333;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h1>WCIA Article Summaries</h1>
            {response_string}
        </body>
        </html>
    """

    return html_template


# str(soup.prettify())