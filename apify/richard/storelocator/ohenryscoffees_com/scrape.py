import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMPANY_URL = "https://ohenryscoffees.com"
CHROME_DRIVER_PATH = 'chromedriver'


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
            "locator_domain",
            "location_name",
            "street_address",
            "city",
            "state",
            "zip",
            "country_code",
            "store_number",
            "phone",
            "location_type",
            "latitude",
            "longitude",
            "hours_of_operation"
        ])
        # Body
        for row in data:
            writer.writerow(row)

def parse_info(store):
    exception_dict = {
        'Samford University, Birmingham, AL':{
            'street_address': '800 Lakeshore Dr. Student Center',
            'city': 'Birmingham',
            'state': 'AL',
            'zip_code': '35229',
            'hour': """Mon-Thurs
            7:00 a.m. - 10:00 p.m.
            Friday
            7:00 a.m.- 2:00 p.m.
            Saturday
            8:00 a.m. - 2:00 p.m.
            Sunday
            Closed
            """,
            'phone_number': '<MISSING>,'
        }
    }

    location_title = store.find_element_by_css_selector('div.textwidget').get_attribute('textContent').strip().split('\n')[0]
    street_address = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[0].strip()

    if location_title in exception_dict.keys():
        street_address = exception_dict[location_title]['street_address']
        city = exception_dict[location_title]['city']
        state = exception_dict[location_title]['state']
        zip_code = exception_dict[location_title]['zip_code']
        phone_number = exception_dict[location_title]['phone_number']
        hour = exception_dict[location_title]['hour']
    elif len(store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')) == 3:
        city = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[0].strip()
        state = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[1].strip().split(' ')[0]
        zip_code = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[1].strip().split(' ')[1]
        phone_number = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[2].strip()
        hour = store.find_element_by_css_selector('div.textwidget > h5').get_attribute('textContent')
    else:
        street_address += store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[1]
        city = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[2].strip().split(',')[0].strip()
        state = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[2].strip().split(',')[1].strip().split(' ')[0]
        zip_code = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[2].strip().split(',')[1].strip().split(' ')[1]
        phone_number = store.find_element_by_css_selector('div.textwidget > p').get_attribute('innerHTML').split('<br>')[3].strip()
        hour = store.find_element_by_css_selector('div.textwidget > h5').get_attribute('textContent')

    return location_title, street_address, city, state, zip_code, phone_number, hour




def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    hours = []
    data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get('https://ohenryscoffees.com/locations/')

    stores = driver.find_elements_by_css_selector('div.panel-layout > div.panel-grid.panel-no-style > div.panel-grid-cell:not(.panel-grid-cell-empty):not(.panel-grid-cell-mobile-last)')

    for store in stores:
        location_title, street_address, city, state, zip_code, phone_number, hour = parse_info(store)
        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        hours.append(hour)
        phone_numbers.append(phone_number)

    # Store data
    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            hour,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        hours,
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone_number,
                '<MISSING>',
                '<MISSING>',
                '<MISSING>',
                hour,
            ]
        )

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()