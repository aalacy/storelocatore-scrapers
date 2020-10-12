from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.glossier.com/'
    ext = 'locations'
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)
    hrefs = driver.find_elements_by_xpath('//a[contains(@href,"/locations?city")]')
    all_store_data = []
    link_list = []

    for h in hrefs:
        link_list.append(h.get_attribute('href'))

    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(5)
        
        cont = driver.find_element_by_css_selector('div.location-description').text.split('\n')
        
        location_name = cont[0]
        street_address = cont[1]
        city_line = cont[2].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = 'US'
        
        hours = ''
        for c in cont[6:]:
            hours += c + ' '
            
        hours = hours.strip()
        if "closed through 2020" in hours:
            hours = "Closed"
        store_number = '<MISSING>'
        phone_number = '<MISSING>'
        location_type = '<MISSING>'

        map_link = driver.find_element_by_css_selector('div.location-description').find_element_by_tag_name("a").get_attribute("href")
        try:
            req = session.get(map_link, headers = HEADERS)
            maps = BeautifulSoup(req.text,"lxml")
            map_link = req.url
            at_pos = map_link.rfind("@")
            lat = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
            longit = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
        except:
            lat = '<MISSING>'
            longit = '<MISSING>'

        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
