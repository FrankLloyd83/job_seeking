import pandas as pd


class JobScrapperManager:
    def __init__(self):
        self.scrapers = []

    def add_scraper(self, scraper):
        self.scrapers.append(scraper)

    def aggregate_results(self):
        all_data = []
        for scraper in self.scrapers:
            all_data.extend(list(scraper.scrape()))
        return pd.DataFrame(
            all_data,
            columns=(
                all_data[0].keys()
                if all_data
                else [
                    "title",
                    "city",
                    "company",
                    "min_salary",
                    "max_salary",
                    "frequency",
                    "date_added",
                ]
            ),
        )

    def to_csv(self, filename):
        df = self.aggregate_results()
        df.to_csv(filename, index=False)
