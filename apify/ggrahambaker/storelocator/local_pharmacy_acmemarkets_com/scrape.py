import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import json



session = SgRequests()

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
    locator_domain = 'https://local.pharmacy.acmemarkets.com/'


    driver = get_driver()
    driver.get(locator_domain)

    states = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
    state_list = []
    for state in states:
        state_list.append(state.get_attribute('href'))


    city_list = []
    loc_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        cities = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')

        for city in cities:
    
            if len(city.get_attribute('href').split('/')) == 6:
                loc_list.append(city.get_attribute('href'))
            else:
                city_list.append(city.get_attribute('href'))
                
                


    for city in city_list:
        driver.get(city)
        driver.implicitly_wait(10)
        locs = driver.find_elements_by_css_selector('a.Teaser-nameLink')
        for loc in locs:
            print(loc.get_attribute('href'))
            loc_list.append(loc.get_attribute('href'))
        



    all_store_data = []

    for i, link in enumerate(loc_list):
        print('--------------')
        print(str(i) + '/' + str(len(loc_list)))
        print(link)   
        
        page = session.get(link)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'html.parser')
        lat = soup.find('meta', itemprop="latitude")['content']
        longit = soup.find('meta', itemprop="longitude")['content']
        
        location_name = soup.find('span', {'class': 'LocationName-geo'}).text
        street_address = soup.find('meta', itemprop="streetAddress")['content']
        
        city = soup.find('meta', itemprop='addressLocality')['content']
        
        
        state = soup.find('abbr', itemprop="addressRegion").text
        
        zip_code = soup.find('span', itemprop="postalCode").text
    
        phone_number = soup.find('span', itemprop="telephone").text
    
        
        hours_json = json.loads(soup.find('div', {'class': 'c-location-hours-details-wrapper'})['data-days'])
    
        hours = ''
        for day_of_week in hours_json:
            day = day_of_week['day']
            if len(day_of_week['intervals']) == 0:
                hours += day + ' Closed '
                continue
            start = day_of_week['intervals'][0]['start']
            end = day_of_week['intervals'][0]['end']
            
            hours += day + ' ' + str(start) + ' : ' + str(end) + ' '
            
        
        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link
        store_number = '<MISSING>'
        
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                            store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

        

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
