from modules.indeed import IndeedScraper
from modules.job_scraper_manager import JobScrapperManager


def main():
    manager = JobScrapperManager()

    indeed_scraper = IndeedScraper("data engineer", "paris", 20)
    manager.add_scraper(indeed_scraper)

    manager.to_csv("data.csv")


if __name__ == "__main__":
    main()
