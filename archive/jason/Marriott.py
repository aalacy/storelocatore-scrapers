"""
Marriott Scraper:
Uses selenium to open website, navigate and save data.

Requires a chromedriver to be in the same directory as the program when it runs.
Chromedriver can be downloaded from https://sites.google.com/a/chromium.org/chromedriver/
"""
import json

from parsel import Selector  # pip install parsel
import pandas as pd  # pip install pandas
import janitor  # pip install pyjanitor
from selenium import webdriver  # pip install selenium
import dataset  # pip install dataset

# create database connection
db = dataset.connect('sqlite:///marriott.db')
# create table
hotels = db['hotels']

# open Chrome and set wait time
# driver = webdriver.Firefox(executable_path='./geckodriver')
driver = webdriver.Chrome(executable_path='./chromedriver')
driver.implicitly_wait(10)


def process_searchterm(term):
    """
    Enter the search term on the page, then through the search
    result pages and save data to the database
    """
    driver.get('https://www.marriott.com/search/default.mi')
    keyword_field = driver.find_element_by_id('keywords')
    keyword_field.clear()
    keyword_field.send_keys(term + u'\ue007')

    while True:
        sel = Selector(driver.page_source)
        [hotels.upsert(json.loads(x), ['lat', 'longitude']) for x in
         sel.xpath('//div[starts-with(@id, "property-record-map-")]/@data-property').extract()]
        try:
            driver.find_element_by_class_name('m-pagination-next').click()
        except Exception as E:
            break


def parse_detail_page(hotel):
    """
    From the data in the database build a search string then select the data from each resulting page.
    Return the dictionary to be stored in the database.
    """
    detail_url = f'https://www.marriott.com/search/hotelQuickView.mi?propertyId={hotel["marshaCode"]}&brandCode={hotel[
        "brand"]}&marshaCode={hotel["marshaCode"]}'
    driver.get(detail_url)
    detail_sel = Selector(driver.page_source)

    item = {
        'locator_domain': 'marriott.com',
        'location_name': detail_sel.xpath('//h2/span/text()').extract_first(),
        'street_address': detail_sel.xpath('//div/@data-address-line1').extract_first(),
        'city': detail_sel.xpath('//div/@data-city').extract_first(),
        'state': detail_sel.xpath('//div/@data-stateprovince').extract_first(),
        'zip': detail_sel.xpath('//div/@data-postal-code').extract_first(),
        'country_code': detail_sel.xpath('//div/@data-country').extract_first(),
        'store_number': hotel['marshaCode'],
        'phone': detail_sel.xpath('//div/@data-contact').extract_first(),
        'location_type': hotel['brand'],
        'naics_code': 'NO-DATA',
        'latitude': hotel['lat'],
        'longitude': hotel['longitude'],
        'hours_or_opperation': 'NO-DATA',
    }
    return item


for location in ['US', 'CA']:
    process_searchterm(location)

for x in hotels.all():
    db['final_results'].upsert(parse_detail_page(x), ['latitude', 'longitude'])

# Create a pandas dataframe from the data
df = pd.DataFrame([x for x in db['final_results'].all()])
column_list = [
    'locator_domain', 'location_name', 'street_address', 'city',
    'state', 'zip', 'country_code', 'store_number', 'phone',
    'location_type', 'naics_code', 'latitude', 'longitude',
    'hours_of_operation'
]

brand_dict = {
    'ak': 'Autograph Collection',
    'al': 'Aloft Hotels',
    'ar': 'AC Hotels',
    'bg': 'Bulgari',
    'br': 'Renaissance Hotels',
    'cy': 'Courtyard',
    'de': 'Delta Hotels and Resorts',
    'ds': 'Design HotelsTM',
    'eb': 'EDITION Hotels',
    'el': 'Element Hotels',
    'er': 'Marriott Executive Apartments',
    'fi': 'Fairfield Inn & Suites',
    'fp': 'Four Points by Sheraton',
    'ge': 'Gaylord Hotels',
    'jw': 'JW Marriott',
    'lc': 'The Luxury Collection',
    'mc': 'Marriott Hotels & Resorts',
    'md': 'Le Méridien',
    'mv': 'Marriott Vacation Club',
    'ox': 'MOXY Hotels',
    'pr': 'Protea Hotels',
    'ri': 'Residence Inn',
    'rz': 'The Ritz-Carlton',
    'sh': 'SpringHill Suites',
    'si': 'Sheraton',
    'ts': 'TownePlace Suites',
    'tx': 'Tribute Portfolio',
    'wh': 'W Hotels',
    'wi': 'Westin Hotels & Resorts',
    'xr': 'St. Regis'
}


def get_brandname(row):
    """
    Convert the brand code given by the website to
    a brand name. If the code isn't in the brand dict,
    return the code.
    """
    try:
        return brand_dict[row.lower()]
    except KeyError:
        return row


def clean_phone(phone):
    """
    Pull all the non-numeric characters from the phone number
    """
    try:
        return ''.join([x for x in phone if x.isnumeric()])
    except TypeError:
        return 'NO-DATA'


# set defaults and apply data cleaning functions
df['hours_of_operation'] = 'NO-DATA'
df['location_type'] = df['location_type'].apply(get_brandname)
df['phone'] = df.phone.apply(clean_phone)

# save to csv
df[column_list].to_csv('marriott_output.csv', index=False)
