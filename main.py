
from datetime import datetime
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
from googletrans import Translator, constants
import re
import indeed_job_info as indeed

# Location, sorting and language
location = "Berlin"
sort_type = "date"
language = "en"
search_query = "Python developer"
query = search_query.replace(" ", "+")
user_agent = '...'





# Change number_of_search_pages to specify how many pages to be scraped
number_of_search_pages = 3

# Constant variables
PAGE_RESULTS_NUMBERS = list(range(0, 300, 10))
URL_SUFFIX_NUMBERS = PAGE_RESULTS_NUMBERS[:number_of_search_pages]


# Time and date variables
now = datetime.now()
current_date = now.strftime("%d/%m/%Y")
current_time = now.strftime("%H:%M:%S")
date_time_list = [current_date, current_time]


def main():
    # Create empty dictionary to store job listing information for each job
    job_dict = {}
    # Creating a running count that will act as a unique ID for each job listing
    count = 1
    # Loop through each page of job adverts
    for search_page in URL_SUFFIX_NUMBERS:
        # Create soup object for current main jobs listing page
        soup = indeed.main_page_setup(search_page, location, sort_type, query,user_agent)
        # Extract job links from page
        job_links = indeed.prepare_job_links(soup)
        # Extract the times each job was posted from the main jobs page
        posted_times = indeed.capture_time_posted(soup)
        # Loop through each link, extract all data from job listing into list and add to dict
        for i, job_link in enumerate(job_links):
            # Create soup object for individual job listing page
            soup = indeed.single_page_setup(job_link)
            # Scrape individual job data from page
            job_data = indeed.scrape_page_data(soup)
            # Insert current date and time
            job_data = date_time_list + posted_times[i] + job_data + [job_links[i]]
            # Add job data to dict
            job_dict[count] = job_data
            # Increment count
            count += 1
    indeed.export_data(job_dict)


if __name__ == '__main__':
    main()