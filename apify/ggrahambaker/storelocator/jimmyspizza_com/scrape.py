import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jimmyspizza_com')



def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' '
    
    if 'PlaceName' in parsed_add:
        city = parsed_add['PlaceName']
    else:
        city = '<MISSING>'
    
    if 'StateName' in parsed_add:
        state = parsed_add['StateName']
    else:
        state = '<MISSING>'
    
    if 'ZipCode' in parsed_add:
        zip_code = parsed_add['ZipCode']
    else:
        zip_code = '<MISSING>'

    return street_address, city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://jimmyspizza.com/'
    ext = 'locator.php'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    select = Select(driver.find_element_by_id('state'))

    opts = driver.find_element_by_css_selector('select#state').find_elements_by_css_selector('option')
    link_list = []
    for opt in opts:
        
        val = opt.get_attribute('value')
        if val == '':
            continue
        
        time.sleep(1)
        select.select_by_value(val)
        driver.implicitly_wait(10)
        time.sleep(1)
        state_select = Select(driver.find_element_by_id('location_address'))
        states = driver.find_element_by_css_selector('select#location_address').find_elements_by_css_selector('option')
        for state in states:
            state_val = state.text
            if 'Choose' in state_val:
                continue
                
            time.sleep(1)
            state_select.select_by_visible_text(state_val)
            loc_link = driver.find_element_by_id('map-link').find_elements_by_css_selector('a')[1].get_attribute('href')
            cont_text =  driver.find_element_by_id('map-link').text

            cont = cont_text.split('\n')
            for c in cont:
                if 'Full Address:' in c:
                    addy = c.replace('Full Address:', '').strip()
                if 'Phone Number:' in c:
                    phone_number = c.replace('Phone Number:', '').strip()
            link_list.append([loc_link, addy, phone_number, state_val])
        
    all_store_data = []
    for link in link_list:
        logger.info(link)
        if '/hawley/' in link[0]:
            driver.get('https://www.jimmyspizzahawley.com/')
        else:
            driver.get(link[0])
            
        driver.implicitly_wait(5)
        time.sleep(5)
        
        addy = link[1]
        if '1115 HWY7' in addy:
            addy = '1115 Hwy 7 W Hutchinson, MN'
        street_address, city, state, zip_code = parse_address(addy)
        logger.info(street_address, city, state, zip_code)
        
        phone_number = link[2]
        
        curr_link = driver.current_url 
        
        if '/sterling/' in curr_link or '/rice/' in curr_link or 'silverbay/' in curr_link or 'stcharles' in curr_link or 'winsted' in curr_link:
            cont = driver.find_element_by_css_selector('div.header-text').text.split('\n')
            hours = ''
            take_more = False
            for c in cont:
                if 'HOURS' in c:
                    take_more = True
                
                if take_more:
                    hours += c + ' '
        
        elif 'jimmyspizzaannandale' in curr_link or 'jimmyspizzacoldspring' in curr_link or 'jimmyspizzahawley' in curr_link or 'immyspizzalitchfield' in curr_link:
            days = driver.find_elements_by_css_selector('div.p.af')
            hours = ''
            for day in days:
                hours += day.text + ' '
                
        elif 'jimmyspizzahutch' in curr_link:
            hours = 'Lunch Mon - Fri 11am-1:30pm Dinner Mon - Thurs 4pm-9pm Fri - Sat 4pm-10pm ​Closed Sunday'
            
        elif 'jimmysaberdeen' in curr_link:
            
            hours = 'Monday – Sunday: 4pm – 9pm'

        else:
            
            hours = driver.find_elements_by_xpath('//div[contains(text(),"STORE HOURS")]')
            if len(hours) == 1:
                hours = hours[0].text.replace('STORE HOURS:', '').replace('\n', ' ')
            else:
                try:
                    hours = driver.find_element_by_xpath('//strong[contains(text(),"Summer Hours")]').find_element_by_xpath('..').text.replace('STORE HOURS:', '').replace('\n', ' ')
                except NoSuchElementException:
                    hours = 'Sunday-Thursday 4pm-10pm Friday & Saturday 4pm-11pm'
                
        hours = hours.replace('STORE HOURS', '').replace('VIEW MENU', '').replace('\n', ' ').strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link[0]
        location_name = link[3]
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
            
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
