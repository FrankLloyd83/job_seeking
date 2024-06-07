import pandas as pd
import string
from .scraper import Scraper


class IndeedScraper(Scraper):
    def __init__(self, keywords="", city="", page_number=1):
        super().__init__("http://fr.indeed.com", keywords, city)
        self.pages_number = page_number
        self.current_page = 0
        self.search_url = self.base_url + f"/emplois?q={self.keywords}&l={self.city}"
        self.contract_types = [
            "cdi",
            "cdd",
            "stage",
            "freelance",
            "intérim",
            "alternance",
        ]

    def find_all_contents(self, soup, tag, class_):
        return soup.find_all(tag, class_=class_) if class_ else soup.find_all(tag)

    def find_element(self, content, tag, class_=None, attrs=None):
        if class_:
            return content.find(tag, class_=class_)
        return content.find(tag, attrs)

    def find_job_id(self, content):
        div_id = self.find_all_contents(
            content,
            "div",
            lambda value: value
            and value.startswith("cardOutline tapItem dd-privacy-allow result job_"),
        )
        if not div_id:
            return None
        classes = div_id[0].get("class")
        for cls in classes:
            if cls.startswith("job_"):
                div_id = cls.split("_")[-1]
                break
        return "IN" + div_id

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

    def find_contract_type(self, content):
        metadata = self.find_all_contents(
            content,
            "div",
            class_="js-match-insights-provider-g6kqeb ecydgvn0",
        )

        if not metadata:
            return None
        for element in metadata:
            if element.text.lower() in self.contract_types:
                return element.text

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

    def find_company_rating(self, content):
        rating = self.find_element(
            content, "span", attrs={"data-testid": "holistic-rating"}
        )
        return rating["aria-label"].split(" ")[0].replace(",", ".") if rating else None

    def get_job_url(self, content):
        url = content.find("a", class_="jcs-JobTitle css-jspxzf eu4oa1w0")
        return self.base_url + url["href"] if url else None

    def find_posted_date(self, content):
        script_soup = [
            s for s in content.find_all("script") if "datePublished" in s.text
        ]
        if not script_soup:
            return None
        script = script_soup[0]
        timestamp_str = (
            script.text.split("datePublished")[1]
            .split(":")[1]
            .split(",")[0]
            .strip()
            .replace('"', "")
        )
        return pd.to_datetime(int(timestamp_str), unit="ms")

    def find_keywords(self, content):
        matching_kw = {}
        description = content.find(
            "div",
            {
                "id": "jobDescriptionText",
                "class": "jobsearch-JobComponent-description css-16y4thd eu4oa1w0",
            },
        )
        if not description:
            return None
        description_text = description.text.lower().translate(
            str.maketrans("", "", string.punctuation)
        )
        words = description_text.split(" ")
        for key, keyword_list in self.kw_list.items():
            matching_kw[key] = {}
            for word, desc in keyword_list.items():
                if word in words:
                    matching_kw[key][word] = desc["mastered"]
        return matching_kw

    def scrape(self):
        while self.current_page < self.pages_number:
            print(
                "Scraping Indeed page",
                self.current_page + 1,
                "out of",
                self.pages_number,
                "...",
            )
            full_url = self.search_url + f"&start={self.current_page * 10}"
            self.current_page += 1
            homepage = self.fetch_page(full_url)
            if not homepage:
                return None

            soup = self.parse_html(homepage)

            contents = self.find_all_contents(soup, "li", "css-5lfssm eu4oa1w0")
            for content in contents:
                if self.find_title(content) is None:
                    continue
                job_id = self.find_job_id(content)
                title = self.find_title(content)
                city = self.find_city(content)
                company = self.find_company(content)
                salary = self.find_salary(content)
                if salary:
                    min_salary, max_salary = self.get_salary_boundaries(salary)
                    frequency = self.get_salary_frequency(salary)
                else:
                    min_salary = max_salary = frequency = None

                rating = self.find_company_rating(content)
                job_url = f"http://fr.indeed.com/viewjob?jk={job_id[2:]}"
                job_page = self.fetch_page(job_url)
                if not job_page:
                    continue

                job_soup = self.parse_html(job_page)
                posted_date = self.find_posted_date(job_soup)
                keywords_dict = self.find_keywords(job_soup)
                contract_type = self.find_contract_type(job_soup)

                yield {
                    "job_id": job_id,
                    "title": title,
                    "city": city,
                    "company": company,
                    "contract_type": contract_type,
                    "min_salary": min_salary,
                    "max_salary": max_salary,
                    "frequency": frequency,
                    "rating": rating,
                    "technical keywords": (
                        list(keywords_dict["technical"].keys())
                        if keywords_dict
                        else None
                    ),
                    "technical keywords mastered count": (
                        int(
                            len(
                                [ms for ms in keywords_dict["technical"].values() if ms]
                            )
                        )
                        if keywords_dict and keywords_dict["technical"]
                        else 0
                    ),
                    "date_scraped": pd.Timestamp.now(),
                    "date_added": posted_date,
                    "job_url": job_url,
                }
