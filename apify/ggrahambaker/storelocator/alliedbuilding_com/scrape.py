import csv
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
    locator_domain = 'http://alliedbuilding.com/'
    ext = 'About/AlliedBranches?div=all#all'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    state_opts = driver.find_element_by_css_selector('select#stval').find_elements_by_css_selector('option')
    link_list = []
    for state in state_opts:
        if 'Select' in state.text:
            continue
            
        url = 'http://alliedbuilding.com/About/AlliedBranches?stval=' + state.text
        link_list.append(url)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(5)
        
        locs = driver.find_elements_by_css_selector('div.BranchBizCard')
        
        for loc in locs:
            loc_html = loc.get_attribute('innerHTML')
            soup = BeautifulSoup(loc_html, 'html.parser')
                   
            location_name = soup.find('a', {'itemprop': 'name'}).text
            
            page_url = locator_domain[:-1] + soup.find('a', {'itemprop': 'name'})['href']

            street_address = soup.find('span', {'itemprop': 'streetAddress'}).text
            city = soup.find('span', {'itemprop': 'addressLocality'}).text
            state = soup.find('span', {'itemprop': 'addressRegion'}).text
            zip_code = soup.find('span', {'itemprop': 'postalCode'}).text
        
            phone_number_spans = soup.find_all('span', {'itemprop': 'telephone'})
            if len(phone_number_spans) == 1:
                phone_number = phone_number_spans[0].text
            else:
                phone_number = '<MISSING>'

            hours_meta = soup.find_all('meta', {'itemprop': 'openingHours'})
            if len(hours_meta) > 0:
                hours = hours_meta[0]['content']
            else:
                
                r_hours_meta = soup.find_all('meta', {'itemprop': 'receivingHours'})
                if len(r_hours_meta) > 0:
                    hours = r_hours_meta[0]['content']
                else:
                    hours = '<MISSING>'
    
            lat_tag = soup.find('meta', {'itemprop': 'latitude'})
            longit_tag = soup.find('meta', {'itemprop': 'longitude'})

            try:
                lat = lat_tag['content']
            except:
                lat = '<MISSING>'

            try:
                longit = longit_tag['content']
            except:
                longit = '<MISSING>'

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
