import requests
import json
from bs4 import BeautifulSoup


class Scraper:
    """
    Base class for all scrapers. Subclasses should implement the scrape method.
    """

    def __init__(self, base_url, keywords="", city=""):
        """
        Initialize the scraper with a base URL, keywords and city.
        :param base_url: The base URL to scrape
        :param keywords: Keywords to search for
        :param city: City to search in
        """
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
        self.kw_list = json.loads(open("resources/kw_list.json").read())

    def fetch_page(self, url):
        """
        Fetch a page from the given URL.
        :param url: The URL to fetch
        :return: The response object
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def detect_encoding(self, response):
        """
        Detect the encoding of the response content.
        :param response: The response object
        """
        content_type = response.headers.get("content-type")
        if "charset=" in content_type:
            self.encoding = content_type.split("charset=")[-1]
        else:
            self.encoding = "utf-8"

    def parse_html(self, response):
        """
        Parse the HTML content of the response.
        :param response: The response object
        :return: The parsed HTML content
        """
        self.detect_encoding(response)
        html_content = response.content.decode(self.encoding)
        return BeautifulSoup(html_content, "html.parser")

    def scrape(self):
        """
        Scrape the base URL for job listings.
        """
        raise NotImplementedError("Subclasses should implement this method")
