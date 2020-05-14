import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.ohiohealth.com/' 
    url = 'https://www.ohiohealth.com/api/findalocation/get?locq=&lat=39.1031182&lng=-84.5120196&dist=1000&endPoint=%2Fapi%2Ffindalocation%2Fget'
    r = session.get(url, headers = HEADERS)

    locs = json.loads(r.content)['results']
    driver = get_driver()

    all_store_data = []
    for loc in locs:
        location_name = loc['Name']
        street_address = loc['AddressLine1']
        
        city = loc['City']
        state = loc['State']
        zip_code = loc['ZipCode']
        
        phone_number = loc['Phone']
        if phone_number == '':
            phone_number = '<MISSING>'
        lat = loc['Latitude']
        longit = loc['Longitude']
        
        page_url = locator_domain + loc['Url']
        
        country_code = 'US'
        store_number = '<MISSING>'
        driver.get(page_url)
        driver.implicitly_wait(5)
        try:
            location_type = driver.find_element_by_css_selector('span.name-title').text
        except:
            try:
                location_type = driver.find_element_by_css_selector('span.specialty-title').text
            except:
       

                location_type = '<MISSING>'

        try:
            hours_soup = driver.find_element_by_css_selector('ul.hours-dropdown').get_attribute('innerHTML')
            
            soup = BeautifulSoup(hours_soup, 'html.parser')
            days = soup.find_all('li')
            if len(days) > 0:
                hours = ''
                for d in days:
                    day = d.find('div', {'class': 'day-label'}).text
                    time = d.find('div', {'class': 'time-label'}).text
                    hours += day + ' ' + time + ' '
            else:
                hours = soup.text
                #hours = 'For office hours at this location, please call the main phone number.'
        except:
            hours = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'

        if phone_number == '':
            phone_number = '<MISSING>'
        
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
  

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
