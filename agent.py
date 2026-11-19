import os
import smtplib
import feedparser
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from dotenv import load_dotenv
from google import genai

load_dotenv()

LOOKBACK_HOURS = 24
MAX_ARTICLES = 40
MODEL = "gemini-3.5-flash-lite"

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed",
]


def fetch_news():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    news_items = []

    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                published_parsed = entry.get("published_parsed")
                if not published_parsed:
                    continue

                published = datetime(*published_parsed[:6], tzinfo=timezone.utc)
                if published < cutoff:
                    continue

                news_items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:300],
                })
        except Exception as e:
            print(f"Error with {feed_url}: {e}")

    return news_items


def summarize(articles):
    if not articles:
        return None

    lines = []
    for a in articles[:MAX_ARTICLES]:
        lines.append(f"- {a['title']} | {a['link']} | {a['summary']}")
    raw_text = "\n".join(lines)

    prompt = (
        "You are an AI news editor. From the articles below, write a daily "
        "AI news digest with the top 5 to 8 stories. Group them by theme, "
        "give each a 2-3 sentence summary, and include its link. "
        "Format the output as simple HTML (use <h3>, <p>, <a>). "
        "Return only the HTML, no code fences.\n\n"
        + raw_text
    )

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


def send_email(html):
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "")

    html = html.replace("html", "").replace("", "").strip()

    today = datetime.now().strftime("%d %b %Y")
    msg = MIMEText(html, "html")
    msg["Subject"] = f"Daily AI News Digest - {today}"
    msg["From"] = user
    msg["To"] = user

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.send_message(msg)
        print("Email sent!")
    except Exception as e:
        print(f"Email error: {e}")


if __name__ == "__main__":
    articles = fetch_news()
    print(f"Got {len(articles)} articles")
    digest = summarize(articles)
    if digest:
        send_email(digest)
    else:
        print("No digest generated, email not sent.")