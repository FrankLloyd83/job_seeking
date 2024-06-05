from modules.indeed import IndeedScraper

scraper = IndeedScraper("python", "paris")
jobs = scraper.scrape()
