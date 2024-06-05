import requests
from bs4 import BeautifulSoup
from .scraper import Scraper


class IndeedScraper(Scraper):
    def __init__(self, keywords="", city=""):
        super().__init__("http://fr.indeed.com/", keywords, city)
        self.full_url = self.base_url + f"emplois?q={self.keywords}&l={self.city}"

    def find_all_contents(self, soup, tag, class_):
        return soup.find_all(tag, class_=class_) if class_ else soup.find_all(tag)

    def find_title(self, content):
        head = content.find("h2", class_="jobTitle css-198pbd eu4oa1w0")
        if head is None:
            return None
        return head.find("span")["title"]

    def find_city(self, content):
        location = content.find(
            "div", {"class": "company_location css-17fky0v e37uo190"}
        )
        if location is None:
            return None
        city = location.find(
            "div", {"data-testid": "text-location", "class": "css-1p0sjhy eu4oa1w0"}
        )
        if city is None:
            return None
        return city.text

    def find_company(self, content):
        location = content.find("div", class_="company_location css-17fky0v e37uo190")
        if location is None:
            return None
        company = location.find(
            "span", {"data-testid": "company-name", "class": "css-63koeb eu4oa1w0"}
        )
        if company is None:
            return None
        return company.text

    def scrape(self):
        # Implémentez le scraping spécifique pour Job Site A
        homepage = self.fetch_page(self.full_url)
        if homepage:
            soup = self.parse_html(homepage)

            contents = self.find_all_contents(soup, "li", "css-5lfssm eu4oa1w0")
            for content in contents:
                if self.find_title(content) is None:
                    continue
                print(
                    self.find_title(content),
                    self.find_city(content),
                    self.find_company(content),
                )
