import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMPANY_URL = "https://paragontheaters.com"
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

def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get('https://paragontheaters.com/locations')

    theaters = driver.find_elements_by_id('theaterBox')

    for theater in theaters:
        # Location name
        locations_titles.append(theater.find_element_by_css_selector('a > h4').get_attribute('textContent'))

        # Street address
        street_addresses.append(theater.find_element_by_css_selector('a > p').get_attribute('innerHTML').split('<br>')[0].strip())

        # City
        cities.append(theater.find_element_by_css_selector('a > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[0])

        # State
        states.append(theater.find_element_by_css_selector('a > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[1].strip().split(' ')[0])

        # Zip code
        zip_codes.append(theater.find_element_by_css_selector('a > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[1].strip().split(' ')[1])

        # Phone
        phone_numbers.append(theater.find_element_by_css_selector('a > p').get_attribute('innerHTML').split('<br>')[2].strip())



    # Store data
    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
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
                'Always open',
            ]
        )

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
