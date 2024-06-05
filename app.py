from modules.scrapper import Scrapper
from modules.indeed import IndeedScrapper

scraper = IndeedScrapper("python", "paris")
jobs = scraper.scrape()
