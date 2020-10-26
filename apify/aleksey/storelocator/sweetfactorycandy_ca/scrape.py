import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=options)
driver2 = webdriver.Chrome('chromedriver', options=options)
BASE_URL = 'http://sweetfactorycandy.ca'
BASE_URL2 = 'http://sweetfactorycandy.ca/contact'

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


def parse_address(addressInfo):
    # AAA__BBB means combination of AAA and BBB
    location_type, total_address = addressInfo.split(':')
    location_type = ' '.join(location_type.split()[1:])
    street_address__city, state__zip = total_address.split(',')

    street_address__city_splitted = street_address__city.split()
    ind = len(street_address__city_splitted)

    street_address = ' '.join(street_address__city_splitted[:ind-1])
    
    city = street_address__city_splitted[ind-1]
    
    state__zip_splitted = state__zip.replace('.','').split()
    state = state__zip_splitted[0]
    zipcode = state__zip_splitted[1:]
    if len(zipcode) == 2:
        zipcode = ' '.join(zipcode)

    country_code =  determine_country_code(state)

    return {
        'street_address': street_address,
        'city': city,
        'zip': zipcode,
        'state': state,
        'country_code': country_code,
        'location_type': location_type
    }

def determine_country_code(state):
    #from state, get country code.
    if state in STATES:
        return 'US'
    elif state in PROVINCES:
        return 'CA'
    else:
        return None

def parse_phone(phoneInfo):
    print(phoneInfo)
    return phoneInfo.split('\n')[1]

def parse_openInfo(openInfo):
    openInfo_splitted = openInfo.split('\n')
    index = len(openInfo_splitted)
    return ','.join(openInfo_splitted[:index-1])

def parse_location_name(location_nameInfo):
    return location_nameInfo.split(':')[1]

def fetch_data():
    data = []
    driver.get(BASE_URL)
    driver2.get(BASE_URL2)
    store = driver.find_element_by_id('woo_contactus-2')

    phoneInfo = store.find_element_by_css_selector('li[class*="phone"]').text
    phone = parse_phone(phoneInfo)
    
    storeInfo = store.find_element_by_css_selector('li[class*="address"]').text
    
    addressInfo, openInfo = storeInfo.split('\n\n')
    
    addressInfo = addressInfo.split('\n')[1]
    address = parse_address(addressInfo)

    hours_of_operation = parse_openInfo(openInfo)

    location_nameInfo = driver2.find_element_by_css_selector('section[class*="entry"]').find_element_by_tag_name('h3').text
    location_name = parse_location_name(location_nameInfo)

    data.append([
        BASE_URL,
        location_name,
        address['street_address'],
        address['city'],
        address['state'],
        address['zip'],
        address['country_code'],
        '<MISSING>',
        phone,
        address['location_type'],
        '<MISSING>',
        '<MISSING>',
        hours_of_operation
    ])

    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
