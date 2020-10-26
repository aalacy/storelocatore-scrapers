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

BASE_URL = 'https://www.stinehome.com/stores'

PROVINCES = {
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

def filter_data(info):
    return info.replace('"','')

def fetch_data():
    data = []
    driver.get(BASE_URL)

    stores = driver.find_elements_by_css_selector('div.results > div.card-body')
    for store in stores:
        store_number = store.get_attribute('id')
        store_info = store.find_element_by_css_selector('input.form-check-input').get_attribute('data-store-info')
        store_info_array = store_info.split('":')[1:13]
        
        print("store_number %s\n" % (store_number))
        # print("store_info %s\n" % (store_info))
        print("==============================================\n")

        store_info_data={}
        el_key='ID'
        excpt = ',","'

        for el in store_info_array:
            if excpt in el:
                el_val = filter_data(el.split(',","')[0])
                print(el_key+":"+el_val)
                store_info_data[el_key] = el_val
                el_key = filter_data(el.split(',","')[1])
            else: 
                el_val = filter_data(el.split(',"')[0])
                print(el_key+":"+el_val)
                store_info_data[el_key] = el_val
                el_key = filter_data(el.split(',"')[1])

        store_info_data['storeHours'] = store_info_data['storeHours'].replace('\\n',',')
        print("store_info_data %s\n" % (store_info_data))
        

        data.append([
            BASE_URL,
            store_info_data['name'],
            store_info_data['address1'],
            store_info_data['city'],
            store_info_data['stateCode'],
            store_info_data['postalCode'],
            store_info_data['countryCode'],
            store_info_data['ID'],
            store_info_data['phone'],
            'stine',
            store_info_data['latitude'],
            store_info_data['longitude'],
            store_info_data['storeHours']
        ])

    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
