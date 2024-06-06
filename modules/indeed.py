import pandas as pd
from .scraper import Scraper


class IndeedScraper(Scraper):
    def __init__(self, keywords="", city=""):
        super().__init__("http://fr.indeed.com", keywords, city)
        self.full_url = self.base_url + f"/emplois?q={self.keywords}&l={self.city}"

    def find_all_contents(self, soup, tag, class_):
        return soup.find_all(tag, class_=class_) if class_ else soup.find_all(tag)

    def find_element(self, content, tag, class_=None, attrs=None):
        if class_:
            return content.find(tag, class_=class_)
        return content.find(tag, attrs)

    def find_title(self, content):
        head = self.find_element(content, "h2", class_="jobTitle css-198pbd eu4oa1w0")
        return head.find("span")["title"] if head else None

    def find_city(self, content):
        location = self.find_element(
            content, "div", class_="company_location css-17fky0v e37uo190"
        )
        return (
            location.find("div", class_="css-1p0sjhy eu4oa1w0").text
            if location
            else None
        )

    def find_company(self, content):
        location = self.find_element(
            content, "div", class_="company_location css-17fky0v e37uo190"
        )
        return (
            location.find(
                "span", {"data-testid": "company-name", "class": "css-63koeb eu4oa1w0"}
            ).text
            if location
            else None
        )

    def find_salary(self, content):
        metadata = self.find_element(
            content,
            "div",
            class_="heading6 tapItem-gutter metadataContainer css-z5ecg7 eu4oa1w0",
        )
        salary = (
            metadata.find(
                "div",
                {
                    "data-testid": "attribute_snippet_testid",
                    "class": "css-1cvvo1b eu4oa1w0",
                },
            )
            if metadata
            else None
        )
        return salary.text if salary else None

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

    def get_job_url(self, content):
        url = content.find("a", class_="jcs-JobTitle css-jspxzf eu4oa1w0")
        return self.base_url + url["href"] if url else None

    def find_posted_date(self, content):
        script = [s for s in content.find_all("script") if "datePublished" in s.text][0]
        timestamp_str = (
            script.text.split("datePublished")[1]
            .split(":")[1]
            .split(",")[0]
            .strip()
            .replace('"', "")
        )
        return pd.to_datetime(int(timestamp_str), unit="ms")

    def scrape(self):
        homepage = self.fetch_page(self.full_url)
        if not homepage:
            return None

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

            job_page = self.fetch_page(self.get_job_url(content))
            if not job_page:
                continue

            job_soup = self.parse_html(job_page)
            posted_date = self.find_posted_date(job_soup)

            yield {
                "title": title,
                "city": city,
                "company": company,
                "min_salary": min_salary,
                "max_salary": max_salary,
                "frequency": frequency,
                "date_scraped": pd.Timestamp.now(),
                "date_added": posted_date,
            }
