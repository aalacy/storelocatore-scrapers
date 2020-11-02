import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/bin/chromedriver', options=options)

BASE_URL = 'https://www.bubbagump.com/locations.asp'
PROVINCES = list({
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'NT': 'Northwest Territories',
    'NS': 'Nova Scotia',
    'NU': 'Nunavut',
    'ON': 'Ontario',
    'PE': 'Prince Edward Island',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'YT': 'Yukon'
}.keys())
STATES = list({
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MP': 'Northern Mariana Islands',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NA': 'National',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VI': 'Virgin Islands',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}.keys())

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def remove_duplicate_white_spaces(string):
    return " ".join(string.split())

def parse_geo(geo):
    lat, lon = [
        item
        for item in geo.split(', ')
    ]
    return lat, lon

def parse_address(address, country_code):
    street_address, address = address.split('\n\n')
    _address, phone = address.split('\n')
    phone = phone.replace('Ph: ', '').replace('(GUMP)', '')
    _address = _address.split()
    if len(_address) == 3:
        zipcode = _address[2]
    else:
        if country_code == 'CA':
            zipcode = " ".join(_address[2:])
        else:
            zipcode = _address[3]
    return {
        'street_address': street_address,
        'zip': zipcode,
        'phone': phone
    }

def determine_country_code(state):
    if state in STATES:
        return 'US'
    elif state in PROVINCES:
        return 'CA'
    else:
        return None

def fetch_data():
    data = []
    driver.get(BASE_URL)
    stores = driver.find_elements_by_css_selector('div[class*="search_panel"]')
    for store in stores:
        location_name = store.find_element_by_css_selector('a.white_chunk_text').text
        location_data = location_name.split(', ')
        city = " ".join([word.capitalize() for word in location_data[0].split()])
        state = location_data[-1]
        country_code = determine_country_code(state)
        if not country_code: continue
        address = store.find_element_by_css_selector('strong').text
        address = parse_address(address, country_code)
        if not re.match(r'[(]{1}\d{3}[)]{1}\s{1}\d{3}[-]{1}\d{4}', address['phone']): continue
        hours_of_operation = " | ".join([
            remove_duplicate_white_spaces(li.text.strip().replace('\n', ' '))
            for li in store.find_elements_by_css_selector('div.location_hours > ul > li')
        ])
        if not len(hours_of_operation):
            hours_of_operation = '<MISSING>'
        lat, lon = parse_geo(store.find_element_by_css_selector('meta[name="geo.position"]').get_attribute('content'))
        data.append([
            'https://www.bubbagump.com/',
            location_name,
            address['street_address'],
            city,
            state,
            address['zip'],
            country_code,
            '<MISSING>',
            address['phone'],
            '<MISSING>',
            lat,
            lon,
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
