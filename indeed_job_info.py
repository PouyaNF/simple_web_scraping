
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd
from googletrans import Translator, constants
import re

# Constant variables
URL_PREFIX = 'https://de.indeed.com'

# init the Google API translator
translator = Translator()

# Time and date variables
now = datetime.now()
file_date = now.strftime("%Y_%m_%d") + '_' + now.strftime("%H_%M_%S")

# Div class selectors
company_class = "icl-u-lg-mr--sm icl-u-xs-mr--xs"
location_class = "icl-u-xs-mt--xs icl-u-textColor--secondary " \
                 "jobsearch-JobInfoHeader-subtitle " \
                 "jobsearch-DesktopStickyContainer-subtitle"

# German to English translations
translations = {
    'Gerade veröffentlicht': 'Just published',
    'Heute': 'Today',
    'vor 1 Tag': '1 day ago',
    'vor 2 Tagen': '2 days ago',
    'vor 3 Tagen': '3 days ago',
    'vor 4 Tagen': '4 days ago',
    'vor 5 Tagen': '5 days ago',
    'vor 6 Tagen': '6 days ago',
    'vor 7 Tagen': '7 days ago',
    'vor 8 Tagen': '8 days ago',
    'vor 9 Tagen': '9 days ago',
    'vor 10 Tagen': '10 days ago',
    'vor 11 Tagen': '11 days ago',
    'vor 12 Tagen': '12 days ago',
    'vor 13 Tagen': '13 days ago',
    'vor 14 Tagen': '14 days ago',
    'Gerade geschaltet': 'Just switched',
    'Vor mehr als 30 Tagen': 'More than 30 days ago',
}


def main_page_setup(search_page, location, sort_type, query, user_agent):
    """Create soup object for main jobs page"""

    # Create a headers dictionary with the custom user agent
    headers = {
        "User-Agent": user_agent
    }

    url = f'https://de.indeed.com/Jobs?q={query}&l={location}&sort={sort_type}' \
          f'&start={search_page}'

    # Send the request with the custom user agent in the headers
    main_jobs_page = requests.get(url, headers=headers).text
    # parsing html using 'lxml' parser and return soap object
    soup = BeautifulSoup(main_jobs_page, 'lxml')
    return soup


def prepare_job_links(soup):
    """Prepare list of job links from header titles"""
    job_links = []
    results = soup.select('div[class*="jobsearch-SerpJobCard unifiedRow"]')
    for i in range(len(results)):
        job_link = f"{URL_PREFIX}{results[i].h2.a['href']}"
        job_links.append(job_link)
    return job_links


def capture_time_posted(soup):
    """Prepare list of times when each job was posted"""
    posted_times = []
    results = soup.select('span[class*="date"]')
    for i in range(len(results)):
        posted_time = results[i].text
        eng_posted_time = translations[posted_time]
        posted_times.append([eng_posted_time])
    return posted_times


def single_page_setup(job_link):
    """Create soup object for individual job page"""
    job_link_url = job_link
    job_information = requests.get(job_link_url).text
    soup = BeautifulSoup(job_information, 'lxml')
    return soup


def scrape_page_data(soup):
    """Scrape data from individual job listing page"""
    title = soup.find('h1').text

    # Handle job listings where company name is not provided
    company_name_provided = soup.find('div', class_=f'{company_class}')
    if company_name_provided:
        company = soup.find('div', class_=f'{company_class}').text
    else:
        company = "N/A"

    location = soup.find('div', class_=f'{location_class}').find_all('div')[-1].text
    job_info = soup.find('div', id="jobDescriptionText").text
    job_info_translated = translator.translate(job_info, src="de")
    email = re.search(r'[\w\.-]+@[\w\.-]+', job_info)
    if email is None:
        email_address = 'Not available'
    else:
        email_address = email.group(0)
    job_data = [title, company, location, job_info, job_info_translated.text, email_address]
    return job_data


def export_data(job_dict):
    """Create DataFrame and export data to CSV file"""
    job_data = pd.DataFrame.from_dict(job_dict, orient='index',
                                      columns=['Date', 'Time', 'Posted', 'Job Title', 'Company',
                                               'Location', 'Job Description', 'Job Description Translated',
                                               'E-Mail Address', 'Job URL'])
    # Export to CSV
    job_data.to_csv(r'output_data/indeed_job_data_{}.csv'.format(file_date))
