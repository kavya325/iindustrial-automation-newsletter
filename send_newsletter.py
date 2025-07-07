import feedparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

SENDER_EMAIL = "siegerintern@gmail.com"
APP_PASSWORD = "bcityfelirupkdow"
RECIPIENTS = ["siegerintern@gmail.com", "kavyaraj922@gmail.com"]

FEED_URLS = [
    "https://www.automationworld.com/rss.xml",
    "https://www.plantautomation-technology.com/rss/news",
    "https://www.textileworld.com/feed/",
    "https://www.warehousingforum.in/feed/",
    "https://www.engineering.com/rss/news",
    "https://www.materialhandling247.com/rss",
    "https://www.automatedbuildings.com/rss/news.xml"
]

LOOKBACK_DAYS = 2

def fetch_recent_articles():
    articles = []
    cutoff = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)
    for url in FEED_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = None
            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed'):
                published = datetime(*entry.updated_parsed[:6])
            if published and published < cutoff:
                continue
            title_lower = entry.title.lower()
            if any(k in title_lower for k in ["automation", "car parking", "warehouse", "textile", "robotics"]):
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': getattr(entry, 'summary', ''),
                    'published': published.strftime('%Y-%m-%d') if published else ''
                })
    return articles

def build_html(articles):
    if not articles:
        return "<p>No new relevant articles found in the last 2 days.</p>"
    html = "<h2>Industrial Automation Daily Newsletter</h2><ul>"
    for art in articles:
        html += f"<li><a href='{art['link']}'><b>{art['title']}</b></a><br><i>{art['published']}</i><br>{art['summary']}</li><br>"
    html += "</ul>"
    return html

def send_email(html_content):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily Industrial Automation News Digest"
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)

    part_html = MIMEText(html_content, "html")
    msg.attach(part_html)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())

if __name__ == "__main__":
    articles = fetch_recent_articles()
    html = build_html(articles)
    send_email(html)
