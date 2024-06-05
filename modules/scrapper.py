import requests
from bs4 import BeautifulSoup

class Scrapper:
    def __init__(self, url):
        self.url = url

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html_content):
        return BeautifulSoup(html_content, 'html.parser')

    def scrape(self):
        raise NotImplementedError("Subclasses should implement this method")