from bs4 import BeautifulSoup
from app import cache
import requests
from dotenv import load_dotenv
import os
import openai
from datetime import date, datetime, timedelta
load_dotenv()

def extract_article_links(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    articles = soup.find_all("a", class_="article-list__gradient-link")
    article_links = list(set(filter(None, [link.get('href') for link in articles])))
    article_links = list(filter(lambda link: link and 'https://www.wcia.com/ciliving-tv' not in link, article_links))
    return article_links

@cache.memoize(timeout=21600, make_name=lambda url: url)
def get_article_summary(url, text):
    messages=[
      {"role": "system", "content": "You are a helpful assistant. Summarize the following messages succinctly if they are interesting. Weather is interesting, but keep it very short. Petty crime, local sports, and primary through high-school news is not interesting. Respond exactly with 'In other news.' if the news is not interesting"},
      {"role": "user", "content": text}
    ]

    openai.api_key = os.getenv("API_KEY")

    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )
    for response in completion.choices:
        if response.message["role"] == "assistant":
            return response.message["content"]
        
def split_article_texts(article_texts):
    interesting_texts = []
    not_interesting_texts = []
    for url, summary in article_texts.items():
        if summary != 'In other news.':
            interesting_texts.append((url, summary))
        else:
            not_interesting_texts.append((url, summary))
    return interesting_texts, not_interesting_texts

def watsons_at_riggs():
    try:
        RIGGS_URL = "https://www.riggsbeer.com/calendar/"
        today = date.today()
        response = requests.get(RIGGS_URL)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        div_id = f"mec-calendar-events-sec-454-{today.strftime('%Y%m%d')}"
        event_div = soup.find("div", {"id": div_id})

        text_to_search = "Watson’s Chicken"
        results = event_div.find_all(text=text_to_search)

        return len(results) > 0
    except:
        return False

def wcia():
    current_time = datetime.now()
    time_threshold = current_time - timedelta(hours=24)

    URL = 'https://www.wcia.com/news/local-news/'
    page = requests.get(URL)
    article_links = extract_article_links(page.content)

    try:
        article_texts = {}
        for url in article_links:
            article_page = requests.get(url)
            article_soup = BeautifulSoup(article_page.content, 'html.parser')
            update_time_str = article_soup.find(class_="article-meta").contents[-2].text.strip()
            update_time_str = update_time_str.replace('Updated: ', '')
            update_time_str = update_time_str[:-4]
            update_time = datetime.strptime(update_time_str, "%b %d, %Y / %I:%M %p")

            if update_time >= time_threshold:
                all_body = article_soup.find(class_="article-content article-body rich-text")
                text = all_body.get_text(strip=True)
                article_texts[url] = get_article_summary(url, text)    

        print('calls completed')
        interesting_texts, not_interesting_texts = split_article_texts(article_texts)

        column1 = []
        column2 = []
        current_column = 1
        for url, summary in interesting_texts:
            if current_column == 1:
                column1.append((url, summary))
                current_column = 2
            else:
                column2.append((url, summary))
                current_column = 1

        split_index = len(not_interesting_texts) // 2
        first_half = not_interesting_texts[:split_index]
        second_half = not_interesting_texts[split_index:]

        response_string_column1 = ""
        for url, summary in column1 + first_half:
            response_string_column1 += f"<p><a href='{url}'>{summary}</a></p>"
        response_string_column2 = ""
        for url, summary in column2 + second_half:
            response_string_column2 += f"<p><a href='{url}'>{summary}</a></p>"
        
        watsons = f"""
            <body>
                <h1>Watsons is at Riggs today</h1>
            </body>""" if watsons_at_riggs() else f"""
            <body>
                <div>Watsons is not at Riggs today</div>
            </body>"""

        html_template = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Arial', sans-serif;
                        background-color: #f5f5f5;
                        padding: 20px;
                        line-height: 1.6;
                    }}
                    h1 {{
                        color: #2f4f4f;
                        font-size: 32px;
                        text-transform: uppercase;
                        margin-bottom: 40px;
                    }}
                    .columns {{
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: space-between;
                    }}
                    .column {{
                         width: 48%;
                    }}
                    p {{
                        margin-bottom: 20px;
                        color: #333;
                        font-size: 18px;
                        font-weight: bold;
                    }}
                    a {{
                        color: #006400;
                        text-decoration: none;
                        transition: color 0.3s;
                    }}
                    a:hover {{
                        color: #8b0000;
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <h1>WCIA Article Summaries</h1>
                <div class="columns">
                    <div class="column">
                        {response_string_column1}
                    </div>
                    <div class="column">
                        {response_string_column2}
                    </div>
                </div>
            </body>
            {watsons}
            <footer>
                <p>Visit our <a href="https://github.com/ribbansmax/chat_scraper">GitHub repository</a> for more information.</p>
            </footer>
            </html>
        """

        return html_template
    except openai.error.ServiceUnavailableError:
        # Handle the service unavailable error
        response_string = "Due to high demand, the service is currently unavailable. Please try again later."

        html_template = f"""
            <html>
            <head>
                <style>
                    /* CSS styles omitted for brevity */
                </style>
            </head>
            <body>
                <h1>WCIA Article Summaries</h1>
                <p>{response_string}</p>
            </body>
            </html>
        """

        return html_template