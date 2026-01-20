import os
import smtplib
import feedparser
from typing import List
from fastmcp import FastMCP
from newspaper import Article
from dotenv import load_dotenv
from newsapi import NewsApiClient
from email.mime.text import MIMEText
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


load_dotenv()

mcp = FastMCP("GeoNews")

api_key = os.environ.get('NEWS_API_KEY')

@mcp.tool()
def fetch_news_headlines(from_date):

    """
    Fetches news from different sources and Articles.

    Arguments: 
        from_date (str): The cutoff date in ISO format (YYYY-MM-DD). 
                         Articles older than this will be ignored.

    Returns: 
        List of the articles found
    """

    client = NewsApiClient(api_key)

    cutoff_date = datetime.fromisoformat(from_date).replace(tzinfo=timezone.utc)

    leaders = 'Jaishankar OR Modi OR "External Affairs Ministry" OR diplomats'
    
    countries = 'China OR Russia OR USA OR Pakistan OR Nepal OR Bangladesh OR "Sri Lanka" OR Myanmar OR Africa OR Europe'
    
    topics = 'Quad OR "Indo-Pacific" OR BRICS OR Rupee'

    query_string = f'(India OR Indian) AND ({leaders} OR {countries} OR {topics})'

    target_domains = (
        'thehindu.com, indianexpress.com, hindustantimes.com, reuters.com, bloomberg.com, aljazeera.com'            
    )

    try:
        response = client.get_everything(
            q = query_string,
            domains = target_domains,
            language = "en",
            sort_by = "publishedAt",
            page_size = 30
        )

        if response and response['status'] == 'ok':
            articles = response['articles']
            article_list = []
            for article in articles:
                published_date = article['publishedAt']
                published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                if published_date >= cutoff_date:
                    name = article['source']['name']
                    author = article['author']
                    title = article['title']
                    url = article['url']
                    content = article['content']
                    article_list.append({
                        'Source': name,
                        'Author': author,
                        'Title': title,
                        'Url': url,
                        'Published Date': published_date,
                        'Content': content
                    })
        return article_list

    except Exception as e:
        print(f"An error Occured {e}")


@mcp.tool()
def fetch_think_tanks_reports(from_date):
    """
    Checks RSS feeds for articles newer than the given date.
    
    Arguments:
        from_date (str): Cutoff date in YYYY-MM-DD format.
    """

    cutoff_date = datetime.fromisoformat(from_date).replace(tzinfo=timezone.utc)
    
    feeds = {
        "The diplomat": "https://thediplomat.com/feed/",
        "Gateway House": "https://www.gatewayhouse.in/feed/",
        "Indian Council of Research on International Economics Relations": "https://icrier.org/feed/",
        "Chahthamhouse" : "https://www.chathamhouse.org/path/83/feed.xml",
        "Center for Policy Research" : "https://cprindia.org/feed/"
    }
    
    latest_updates = []

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]:
                published_date = entry.get("published")
                published_date = parsedate_to_datetime(published_date)
                if published_date >= cutoff_date:
                    latest_updates.append({
                        "source": source,
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", "Unknown Date")
                    })
        except Exception as e:
            print(f"Error fetching {source}: {e}")

    return latest_updates


@mcp.tool()
def get_article_content(url_list : List[dict[str, str]]) -> List[dict[str,str]]:

    """
    Scrapes full text from a list of URLs.
    Args:
        url_list: List of dictonaries containing the 'topic' and its corrosponding 'url'.
    """

    final_articles = []
    for item in url_list:
        url = item.get('url')
        topic = item.get('topic')
        article = Article(url)
        article.download()
        article.parse()
        final_articles.append({
            'topic' : topic,
            'url' : url,
            'content' : article.text
        })

    return final_articles

@mcp.tool()
def publish_via_email(recipient: str, subject: str, content: str):
    """
    Sends the final formatted newsletter via Gmail.
    """
    sender = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASS')
    
    msg = MIMEText(content, 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)
    
    return "Newsletter sent successfully."

if __name__ == "__main__":
    mcp.run()
