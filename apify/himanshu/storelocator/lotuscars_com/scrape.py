import csv
from sgrequests import SgRequests
import json
import re
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lotuscars_com')





session = SgRequests()

COMPANY_URL = "https://www.lotuscars.com"


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
                "page_url"
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_id = []
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    countries = []
    phone_numbers = []
    latitude_list = []
    longitude_list = []
    hours = []
    data = []
    page_urls = []

    dealers = json.loads(session.get(
        "https://www.lotuscars.com/app/wp-admin/admin-ajax.php?action=dealer_map_load").content)

    for dealer in dealers:
        if dealer['country'] in ['US', 'CA']:
            # Name
            locations_titles.append(dealer['name'])

            # ID
            locations_id.append(dealer['id'])
            add = dealer['address'].split("<br/>")
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(add)))

            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(add)))
            if us_zip_list:
                zipcode = us_zip_list[-1].strip()
            if ca_zip_list:
                zipcode = ca_zip_list[-1].strip()
            # logger.info(zipcode)

            if len(add) == 4:
                street_address = add[0].strip()
                if len(add[1].split(',')) > 1:

                    city = add[1].split(',')[0].strip()
                    state = add[1].split(',')[-1].strip()
                else:
                    city = add[1].strip()
                    if len(add[2].split()[0]) == 2:
                        state = add[2].split()[0]
                    else:
                        state = "<MISSING>"
            else:
                street_address = add[0].strip()
                city = add[1].strip().split(',')[0].strip()
                if len(add[2].split(',')) > 1:
                    state = add[2].split(',')[-1].strip()
                else:
                    state = add[2].strip()
            street_addresses.append(street_address)

            # City
            cities.append(city)

            # State
            states.append(state)

            # Zip code
            zip_codes.append(zipcode)

            # Country
            countries.append(dealer['country'])

            # Phone
            if dealer['phone']:
                phone_numbers.append(dealer['phone'][0]['number'])
            else:
                phone_numbers.append('<MISSING>')

            # Lat
            latitude_list.append(dealer['location']['lat'])

            # long
            longitude_list.append(dealer['location']['lng'])

            # Hour
            # logger.info(dealer["opening_times"])
            try:
                for value in dealer["opening_times"]:
                    hours.append(" ".join(list(BeautifulSoup(
                        value["times"], "lxml").stripped_strings)).strip())

            except:
                hours.append('<MISSING>')
            page_url = dealer["link"]
            if "http://" == page_url:
                page_url = "<MISSING>"

            page_urls.append(page_url)

    # Store data
    for (
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            phone_number,
            country,
            latitude,
            longitude,
            location_id,
            hour,
            page_url

    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        countries,
        latitude_list,
        longitude_list,
        locations_id,
        hours,
        page_urls
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                country,
                location_id,
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                hour,
                page_url
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
