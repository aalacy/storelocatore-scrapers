import csv
import os
from sgselenium import SgSelenium
import json
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://pfchangs.ca/'
    driver = SgSelenium().chrome()

    loc = 'https://pfchangs.ca/locations/'
    driver.get(loc)
    scripts = driver.find_elements_by_css_selector('script')

    all_store_data = []
    for s in scripts:
        if '{var map1 = $("#map1")' in s.get_attribute('innerHTML'):
            cont = s.get_attribute('innerHTML')
            start = cont.find('.maps(') + 6
            end = cont.find(').data("wpgmp_ma')
            loc_data = json.loads(cont[start: end])
            for place in loc_data['places']:
                store_number = place['id']
                location_name = place['title']
                street_address = place['address'].split(',')[0]
                soup = BeautifulSoup(place['content'], 'html.parser')
                phone_number = soup.find('a').text
                
                lat = place['location']['lat']
                longit = place['location']['lng']
                city = place['location']['city']
                state = place['location']['state']
                zip_code = place['location']['postal_code']
                country_code = 'CA'
                
                location_type = '<MISSING>'
                hours = '<MISSING>'
                page_url = '<MISSING>'
                
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
