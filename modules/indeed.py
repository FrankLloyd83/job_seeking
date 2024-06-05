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

    def find_salary(self, content):
        metadata = content.find(
            "div",
            class_="heading6 tapItem-gutter metadataContainer css-z5ecg7 eu4oa1w0",
        )
        if metadata is None:
            return None

        salary = metadata.find(
            "div",
            {
                "data-testid": "attribute_snippet_testid",
                "class": "css-1cvvo1b eu4oa1w0",
            },
        )
        if salary is None:
            return None
        return salary.text

    def get_salary_boundaries(self, salary):
        boundaries = salary.split("€")[:-1]
        if len(boundaries) == 1:
            min_salary = max_salary = "".join(filter(str.isdigit, boundaries[0]))

        for boundary in boundaries:
            if "de" in boundary.lower():
                min_salary = "".join(filter(str.isdigit, boundary))
            elif "à" in boundary.lower():
                max_salary = "".join(filter(str.isdigit, boundary))
        try:
            return min_salary, max_salary
        except UnboundLocalError:
            return None, None

    def get_salary_frequency(self, salary):
        frequency = salary.split(" ")[-1]
        frequency_map = {"mois": "mensuel", "an": "annuel"}
        return frequency_map.get(frequency, "non spécifié")

    def scrape(self):
        homepage = self.fetch_page(self.full_url)
        if homepage:
            soup = self.parse_html(homepage)

            contents = self.find_all_contents(soup, "li", "css-5lfssm eu4oa1w0")
            for content in contents:
                if self.find_title(content) is None:
                    continue
                title = self.find_title(content)
                city = self.find_city(content)
                company = self.find_company(content)
                salary = self.find_salary(content)
                if salary:
                    min_salary, max_salary = self.get_salary_boundaries(salary)
                    frequency = self.get_salary_frequency(salary)
                else:
                    min_salary = max_salary = frequency = None
                print(
                    f"Title: {title}",
                    f"City: {city}",
                    f"Company: {company}",
                    f"Salary: {min_salary} - {max_salary} {frequency}",
                )
