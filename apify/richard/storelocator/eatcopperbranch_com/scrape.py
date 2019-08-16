import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


COMPANY_URL = "https://eatcopperbranch.com"
CHROME_DRIVER_PATH = "chromedriver"


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
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
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    store_numbers = []
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    latitude_list = []
    longitude_list = []
    hours = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get('https://eatcopperbranch.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en&t=1565644279976')
    lists = BeautifulSoup(driver.page_source)

    for item in lists.find_all('item'):
        location_title = item.location.renderContents().decode('utf-8') if item.location.renderContents() else '<MISSING>'
        street_address = item.address.renderContents().decode('utf-8') if item.address.renderContents() else '<MISSING>'
        latitude = item.latitude.renderContents().decode('utf-8') if item.latitude.renderContents() else '<MISSING>'
        longitude = item.longitude.renderContents().decode('utf-8') if item.longitude.renderContents() else '<MISSING>'
        phone_number = item.telephone.renderContents().decode('utf-8') if item.telephone.renderContents() else '<MISSING>'

        hour = item.operatinghours.renderContents().decode('utf-8').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        hour = re.sub('<[^>]*>', '', hour) if hour != re.sub('<[^>]*>', '', hour) else '<MISSING>'

        # Location title
        locations_titles.append(location_title.replace('&amp', '').replace(';#44;', '')) if location_title.replace('&amp', '').replace(';#44;', '') != '' else locations_titles.append('<MISSIG>')

        # Street Address
        street_addresses.append(street_address.replace('&amp', '').replace(';#44;', '').strip().split(',')[0].strip().split('  ')[0].strip()) if street_address.replace('&amp', '').replace(';#44;', '').strip().split('  ')[-1].strip()[:-7] != '' else street_addresses.append('<MISSIG>')

        # City
        cities.append(street_address.replace('&amp', '').replace(';#44;', '').strip().split(',')[0].strip().split('  ')[1].strip()) if street_address.replace('&amp', '').replace(';#44;', '').strip().split('  ')[-1].strip()[:-7] != '' else cities.append('<MISSIG>')

        # Province
        states.append(street_address.replace('&amp', '').replace(';#44;', '').strip().split('  ')[-1].strip()[:-7]) if street_address.replace('&amp', '').replace(';#44;', '').strip().split('  ')[-1].strip()[:-7] != '' else states.append('<MISSIG>')

        # Zip code
        zip_codes.append(street_address.replace('&amp', '').replace(';#44;', '').strip().split('  ')[-1].strip()[-7:]) if street_address.replace('&amp', '').replace(';#44;', '').strip().split('  ')[-1].strip()[-7:] != '' else zip_codes.append('<MISSIG>')

        # Latitude
        latitude_list.append(latitude) if latitude != '' else latitude_list.append('<MISSING>')

        # Longitude
        longitude_list.append(longitude) if longitude != '' else longitude_list.append('<MISSING>')

        # Phone
        phone_numbers.append(phone_number) if phone_number != '' else phone_numbers.append('<MISSING>')

        # Hour
        hours.append(hour) if hour != '' else hours.append('<MISSING>')

    # Store data
    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            latitude,
            longitude,
            hour,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                "CA",
                "<MISSING>",
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                hour,
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()