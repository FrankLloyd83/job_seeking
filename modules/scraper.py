import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self, base_url, keywords="", city=""):
        self.base_url = base_url
        self.keywords = keywords
        self.city = city
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive",
            "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6",
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def detect_encoding(self, response):
        content_type = response.headers.get("content-type")
        if "charset=" in content_type:
            self.encoding = content_type.split("charset=")[-1]
        else:
            self.encoding = "utf-8"

    def parse_html(self, response):
        self.detect_encoding(response)
        html_content = response.content.decode(self.encoding)
        return BeautifulSoup(html_content, "html.parser")

    def scrape(self):
        raise NotImplementedError("Subclasses should implement this method")
