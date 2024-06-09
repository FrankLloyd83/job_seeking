import pandas as pd


class JobScrapperManager:
    """
    Class to manage multiple job scrapers and aggregate their results into a single DataFrame.
    """
    def __init__(self):
        """
        Initialize the JobScrapperManager with an empty list of scrapers.
        """
        self.scrapers = []

    def add_scraper(self, scraper):
        """
        Add a scraper to the list of scrapers.
        :param scraper: The scraper to add
        """
        self.scrapers.append(scraper)

    def aggregate_results(self):
        """
        Aggregate the results of all scrapers into a single DataFrame.
        :return: The aggregated DataFrame
        """
        all_data = []
        for scraper in self.scrapers:
            all_data.extend(list(scraper.scrape()))
        return pd.DataFrame(
            all_data,
            columns=(
                all_data[0].keys()
                if all_data
                else [
                    "job_id",
                    "title",
                    "city",
                    "company",
                    "contract_type",
                    "min_salary",
                    "max_salary",
                    "frequency",
                    "rating",
                    "technical keywords",
                    "technical keywords mastered count",
                    "date_scraped",
                    "date_added",
                    "job_url",
                ]
            ),
        )

    def to_csv(self, filename):
        """
        Save the aggregated results to a CSV file.
        :param filename: The name of the file to save the results to
        """
        df = self.aggregate_results()
        try:
            existing_df = pd.read_csv(filename)
        except FileNotFoundError:
            existing_df = None
        if existing_df is not None:
            df = pd.concat([existing_df, df], ignore_index=True)
        df = df.drop_duplicates(subset=["job_id"])
        df.to_csv(
            filename,
            index=False,
        )
