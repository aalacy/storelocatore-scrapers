import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.waxingthecity.com/"
CHROME_DRIVER_PATH = "chromedriver"

# ZM See if you can abstract out methods like this one 
# in a base class to reuse them
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

# ZM If you are not using a method that is implemented in your code
# it is best to remove it to avoid confusion
def parse_info(item):
    item = item.split("\n")
    location_title = item[0]
    hours = item[-2].replace("Closed Now", "")
    phone = item[-4]
    city = item[-5].split(",")[0]
    state = item[-5].split(",")[1].strip().split(" ")[0]
    zip_code = item[-5].split(",")[1].strip().split(" ")[1]
    if len(item) == 7:
        address = item[1]
    else:
        address = item[1] + " " + item[2]

    return location_title, address, city, state, zip_code, phone, hours


def fetch_data():
    # store data
    locations_titles = []
    location_ids = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    countries = []
    phone_numbers = []
    hours = []
    longitude_list = []
    latitude_list = []
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = "https://momentfeed-prod.apigee.net/api/llp.json?auth_token=GXDJFRKFGUIUJVSV&center=41.2524,-95.998&coordinates=-9.96885060854611,-37.08984375,70.4367988185464,-154.86328125&multi_account=false&page=1&pageSize=1000"
    driver.get(store_url)

    stores = json.loads(driver.find_element_by_css_selector("pre").text)

    for store in stores:
        # Location name
        locations_titles.append(store["store_info"]["name"])

        # Store id
        location_ids.append(store["store_info"]["corporate_id"])

        # Address
        street_addresses.append(
            store["store_info"]["address"]
            + store["store_info"]["address_extended"]
            + store["store_info"]["address_3"]
        )

        # City
        cities.append(store["store_info"]["locality"])

        # State
        states.append(store["store_info"]["region"])

        # Zip
        zip_codes.append(store["store_info"]["postcode"])

        # Country
        countries.append(store["store_info"]["country"])

        # Phone
        phone_numbers.append(store["store_info"]["phone"])

        # Hour
        hours.append(store["store_info"]["store_hours"])

        # Lat
        latitude_list.append(store["store_info"]["latitude"])

        # Long
        longitude_list.append(store["store_info"]["longitude"])

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
        country,
        location_id,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
        countries,
        location_ids,
    ):
        if "coming soon" in locations_title.lower():
            pass
        else:
            # ZM if you are checking for non-empty values you can just 
            # do "if variable"
            data.append(
                [
                    COMPANY_URL if COMPANY_URL != "" else "<MISSING>",
                    locations_title if locations_title != "" else "<MISSING>",
                    street_address if street_address != "" else "<MISSING>",
                    city if city != "" else "<MISSING>",
                    state if state != "" else "<MISSING>",
                    zipcode if zipcode != "" else "<MISSING>",
                    country if country != "" else "<MISSING>",
                    location_id if location_id != "" else "<MISSING>",
                    phone_number if phone_number != "" else "<MISSING>",
                    "<MISSING>",
                    latitude if latitude != "" else "<MISSING>",
                    longitude if longitude != "" else "<MISSING>",
                    hour if hour != "" else "<MISSING>",
                ]
            )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
