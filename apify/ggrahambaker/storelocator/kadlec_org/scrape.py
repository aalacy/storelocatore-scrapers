import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
import time
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kadlec_org')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetNamePreType' in parsed_add:
        street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
        
    if 'PlaceName' not in parsed_add:
        city = '<MISSING>'
    else:
        city = parsed_add['PlaceName']
    
    if 'StateName' not in parsed_add:
        state = '<MISSING>'
    else:
        state = parsed_add['StateName']
        
    if 'ZipCode' not in parsed_add:
        zip_code = '<MISSING>'
    else:
        zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.kadlec.org/'
    ext = 'location-directory/search-results?type=6AE71E0E461F48429DCE5A11C5EC0CF2'

    driver = SgSelenium().chrome()

    driver.get(locator_domain + ext)
    driver.implicitly_wait(5)
    time.sleep(5)

    opts = driver.find_element_by_id('psjh_body_1_psjh_twocol_cellone_0_locationType').find_elements_by_css_selector('option')
    types = []
    for opt in opts:
        o = opt.get_attribute('value').strip()
        if 'Select' in o:
            continue
        types.append([o, opt.text])

    link_list = []
    for t in types:
        select = Select(driver.find_element_by_id('psjh_body_1_psjh_twocol_cellone_0_locationType'))
        
        select.select_by_value(t[0])
        driver.find_element_by_css_selector('button.btn.btn-primary.pull-right').click()
        driver.implicitly_wait(5)
        time.sleep(3)

        while True: 
            main = driver.find_element_by_css_selector('ul.list-unstyled.row')
            lis = main.find_elements_by_css_selector('li')
            links = [li.find_element_by_css_selector('a').get_attribute('href') for li in lis ]
            for l in links:
                link_list.append([l, t[1]])
            eles = driver.find_elements_by_xpath('//a[contains(text(),"Next")]')
            
            if len(eles) == 0:
                break
                                    
            next_link = driver.find_elements_by_xpath('//a[contains(text(),"Next")]')[0].get_attribute('href')
            driver.get(next_link)
            driver.implicitly_wait(5)
            
    all_store_data = []
    for link in link_list:
        logger.info(link[0])
        driver.get(link[0])
        
        driver.implicitly_wait(5)
        
        info = driver.find_elements_by_css_selector('div.location-contactus-list__inner')
        
        if len(info) == 2:
            sec = info[1]
            
            location_name = sec.find_element_by_css_selector('h4#psjh_body_2_psjh_twocol_celltwo_0_locationsContactUs_nameContainer_0').text
            
            addy = sec.find_element_by_css_selector('div#psjh_body_2_psjh_twocol_celltwo_0_locationsContactUs_addressContainer_0').text
            
            hours = sec.find_elements_by_css_selector('div#psjh_body_2_psjh_twocol_celltwo_0_locationsContactUs_locationHoursContainer_0')
            if len(hours) == 1:
                hours = hours[0].text.replace('\n', ' ').strip()
                hours = ' '.join(hours.split())
            else:
                hours = '<MISSING>'
                
            phone_numbers = sec.find_elements_by_css_selector('div#psjh_body_2_psjh_twocol_cellone_0_locationPhoneContainer')
            if len(phone_numbers) > 0:
                phone_number = phone_numbers[0].text.replace('Phone:', '').strip()
            else:
                phone_numbers = sec.find_elements_by_css_selector('div#psjh_body_2_psjh_twocol_celltwo_0_locationsContactUs_locationPhoneContainer_0')
                if len(phone_numbers) > 0:
                    phone_number = phone_numbers[0].text.replace('Phone:', '').strip()
                else:
                    phone_number = '<MISSING>'
        
        else:
            location_name = driver.find_element_by_css_selector('h1#psjh_body_2_psjh_twocol_cellone_0_nameContainer').text
            addy = driver.find_element_by_css_selector('div#psjh_body_2_psjh_twocol_cellone_0_addressContainer').text.split('\n')[1]
            phone_number = driver.find_element_by_css_selector('div#psjh_body_2_psjh_twocol_cellone_0_locationPhoneContainer').text.replace('Phone:', '').strip()
            
            hours = driver.find_element_by_css_selector('div#psjh_body_2_psjh_twocol_cellone_0_locationHoursContainer').text.replace('Hours:', '').strip()
    
        if '780 Swift Blvd.' in addy:
            addy = ' 780 Swift Blvd. Richland, WA 99352'
        if '1100 Goethals Drive, ' in addy:
            addy = '1100 Goethals Drive, Richland, WA 99352'
        street_address, city, state, zip_code = parse_address(addy)
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = link[1]
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link[0]
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        logger.info(store_data)
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
