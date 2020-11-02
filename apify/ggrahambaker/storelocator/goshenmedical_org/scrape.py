import csv
import os
from sgselenium import SgSelenium

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://goshenmedical.org/' 
    ext = 'allcounties.html'

    driver = SgSelenium().chrome()

    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('table.table-padding')
    locs = main.find_elements_by_css_selector('tr')

    link_list = []
    for l in locs:
        cols = l.find_elements_by_css_selector('td')
        if len(cols) == 1:
            continue
        for c in cols:
            info = c.text.split('\n')
            
            links = c.find_elements_by_css_selector('img')
            if len(links) == 0:
                break
            location_name = info[0]
            street_address = info[1]
            city, state, zip_code = addy_ext(info[2])
   
            link = links[0].find_element_by_xpath('..').get_attribute('href')
            link_list.append([link, location_name, street_address, city, state, zip_code])
            
    all_store_data = []
    for link in link_list:
        driver.get(link[0])
        driver.implicitly_wait(5)
        hours_table = driver.find_element_by_css_selector('td.white-text').find_element_by_css_selector('table')
        
        rows = hours_table.find_elements_by_css_selector('tr')
    
        days = rows[0].find_elements_by_css_selector('td')
        times = rows[1].find_elements_by_css_selector('td')
        hours = ''
        for i, day in enumerate(days):
            hours += days[i].text + ' ' + times[i].text + ' '
        
        if len(rows) > 2:
            extra = rows[2].text
            hours += extra 
        
        hours = ' '.join(hours.split())
        
        phone_number = driver.find_element_by_xpath('//u[contains(text(),"Phone Number")]').find_element_by_xpath('../..').text.split('\n')[1]
        page_url, location_name, street_address, city, state, zip_code = link
        street_address = street_address.split('Suite')[0].strip().replace(',', '').strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
