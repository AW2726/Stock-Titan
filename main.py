import requests
from bs4 import BeautifulSoup
import time

WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"
STOCKTITAN_URL = "https://www.stocktitan.net/news/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

seen_links = set()

def fetch_news():
    res = requests.get(STOCKTITAN_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.select("div.news-card__item")

    new_posts = []

    for article in articles:
        link_tag = article.find("a", href=True)
        tag_list = article.select(".news-card__label")

        tags = [t.get_text(strip=True).lower() for t in tag_list]
        if "nasdaq" not in tags:
            continue

        if link_tag:
            url = "https://www.stocktitan.net" + link_tag["href"]
            title = article.get_text(strip=True)
            if url not in seen_links:
                seen_links.add(url)
                new_posts.append((title, url))
    
    return new_posts

def post_to_discord(posts):
    for title, url in posts:
        data = {"content": f"📢 **{title}**\n{url}"}
        requests.post(WEBHOOK_URL, json=data)

def main():
    while True:
        print("Checking for new NASDAQ-tagged news...")
        new_news = fetch_news()
        if new_news:
            print(f"Posting {len(new_news)} new articles to Discord.")
            post_to_discord(new_news)
        time.sleep(300)

if __name__ == "__main__":
    main()
