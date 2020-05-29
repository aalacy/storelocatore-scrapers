import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
    parsed_add = usaddress.tag(addy)[0]

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
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' ' 

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.mcalistersdeli.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    states = driver.find_element_by_css_selector('div.national-list').find_elements_by_css_selector('a')
    state_links = []
    for state in states:
        state_link = state.get_attribute('href')
        state_links.append(state_link)

    loc_list = []
    for state in state_links:
        driver.get(state)
        driver.implicitly_wait(10)
        cities = driver.find_element_by_css_selector('div.state-national-list').find_elements_by_css_selector('a')
        for city in cities:
            city_link = city.get_attribute('href')
            loc_list.append(city_link)    
            
    link_list = []
    for loc in loc_list:
        driver.get(loc)
        driver.implicitly_wait(10)

        main = driver.find_element_by_css_selector('div.city-list').find_element_by_css_selector('ul')
        locs = main.find_elements_by_css_selector('li')
        for loc in locs:
            loc_links = loc.find_elements_by_css_selector('a')
            link = loc_links[0].get_attribute('href')
            loc_name = loc_links[0].text
            phone_number = loc_links[1].get_attribute('href').replace('tel:', '')
            
            link_list.append([link, loc_name, phone_number])    

    all_store_data = []
    dup_tracker = []
    for i, data in enumerate(link_list):
        driver.get(data[0])
        if data[0] not in dup_tracker:
            dup_tracker.append(data[0])
        else:
            continue
        if 'humble/9477-fm-1960-bp-100-101000' in data[0]:
            continue
        driver.implicitly_wait(10)
        print('----------')
        print(data[0])
        print(str(i) + '/' + str(len(link_list)))
        print()

        addy_a = driver.find_element_by_xpath("//a[contains(@href, 'maps.google.com/?daddr')]")
        map_href = addy_a.get_attribute('href')
        map_link_start = map_href.find('?daddr=')
        addy = map_href[map_link_start + 7:].replace('+', ' ')

        if '99 Eglin Parkway NE Ft.' in addy:
            street_address = '99 Eglin Parkway NE'
            city = 'Ft. Walton Beach'
            state = 'FL'
            zip_code = '32547'
        elif '1006 University Dr. East' in addy:
            street_address = '1006 University Dr. East'
            city = 'College Station'
            state = 'TX'
            zip_code = '77840'
        elif '620 University Shopping Center' in addy:
            street_address = '620 University Shopping Center'
            city = 'Richmond'
            state = 'KY'
            zip_code = '40475'
        elif '8670 Veterans Memorial Parkway' in addy:
            street_address = '8670 Veterans Memorial Parkway'
            city = "O'Fallon"
            state = 'MO'
            zip_code = '63366'
        elif 'Bank of America Plaza' in addy:
            street_address = 'Bank of America Plaza'
            city = "Charlotte"
            state = 'NC'
            zip_code = '28280'
        elif '70 Riverton Commons Plaza' in addy:
            street_address = '70 Riverton Commons Plaza, Suite B-100'
            city = "Front Royal"
            state = 'VA'
            zip_code = '22630'

        else:
            street_address, city, state, zip_code = parse_addy(addy)
        
        map_link = driver.find_element_by_xpath('//a[contains(text(),"see map")]')

        lat = map_link.get_attribute('data-lat')
        longit = map_link.get_attribute('data-long')
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        try:
            hours = driver.find_element_by_css_selector('div.hours-wrapper').text.replace('\n', ' ').replace('hours', '').strip()
            for day in days:
                if day in hours:
                    continue
                else:
                    hours = hours.replace('Today', day)
        except NoSuchElementException:
            hours = '<MISSING>'
        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = data[0]
        store_number = '<MISSING>'
        location_name = data[1]
        phone_number = data[2]
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
