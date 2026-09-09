import requests
from bs4 import BeautifulSoup

def find_leads():
    urls = ["https://www.startupradar.io", "https://www.crunchbase.com"]
    leads = []
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for link in soup.find_all("a", href=True):
                if "cyber" in link["href"] or "security" in link["href"]:
                    leads.append(link["href"])
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return leads
