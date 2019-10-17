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

BASE_URL = 'https://www.swervefitness.com/contact'

PROVINCES = {
    'AB': 'Alberta',                                                                                     'BC': 'British Columbia',
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
}
STATES = {
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
}

character_allowed = [ '_', '-', '$', ',', '(', ')', '+']
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


def determine_country_code(state):
    #from state, get country code.
    if state in STATES:
        return 'US'
    elif state in PROVINCES:
        return 'CA'
    else:
        return None

def parse_phone(phoneInfo):
    if phoneInfo[-1].isdigit():
         return phoneInfo
    return phoneInfo[:-1]


def parse_openInfo(openInfo):
    openInfo_splitted = openInfo.split('\n')
    index = len(openInfo_splitted)
    return ','.join(openInfo_splitted[:index-1])

def parse_location_name(location_nameInfo):
    return location_nameInfo.split(':')[1]

def fetch_data():
    data = []
    driver.get(BASE_URL)

    stores = driver.find_elements_by_css_selector('td[style*="text-align: center;"]')
    for store in stores:
        
        storeInfo = store.text.split('\n')
        location_name = storeInfo[0]
        street_address = ' '.join(storeInfo[1:2])
        state__zip = remove_duplicate_white_spaces(storeInfo[3].split(',')[1])
        phoneInfo = storeInfo[4]
        phone = parse_phone(phoneInfo)
        
        state__zip_splitted = state__zip.split(' ')
        state = state__zip_splitted[0]
        city = '<MISSING>'
        if state in STATES:
            city = STATES[state]
        zip = state__zip_splitted[1][:5]

        country_code =  determine_country_code(state)

        data.append([
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            '<MISSING>',
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])

    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
