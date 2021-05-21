import csv
import re
import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("flooranddecor_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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

    base_link = "https://www.flooranddecor.com/view-all-stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "openingHours" in str(script):
            script = str(script)
            break

    all_states = re.findall(r"States\.push\(new Array\(\'[A-Z]{2}", script)

    data = []

    for search in all_states:
        link = (
            "https://www.flooranddecor.com/store-results?searchTerm=%s&cityLatitude=&cityLongitude=&_=1621403580607"
            % (search.split("'")[1][:2])
        )

        logger.info(link)

        req = session.get(link, headers=headers)
        time.sleep(2)
        if req.status_code != 403:
            try:
                state_data = req.json()
            except:
                continue

            stores = state_data["stores"]
            for store in stores:
                locator_domain = "flooranddecor.com"
                location_name = store["name"]
                street_address = store["address1"]
                city = store["city"]
                state = store["stateCode"]
                zip_code = store["postalCode"]
                country_code = "US"
                store_number = store["ID"]
                phone = store["phone"]
                location_type = store["storeStatus"]

                raw_hours = store["storeHours"]
                hours_of_operation = BeautifulSoup(raw_hours, "lxml").getText(" ")
                if not hours_of_operation:
                    hours_of_operation = "<MISSING>"

                latitude = store["latitude"]
                longitude = store["longitude"]

                link = "https://www.flooranddecor.com/store?StoreID=" + store_number

                data.append(
                    [
                        locator_domain,
                        link,
                        location_name,
                        street_address,
                        city,
                        state,
                        zip_code,
                        country_code,
                        store_number,
                        phone,
                        location_type,
                        latitude,
                        longitude,
                        hours_of_operation,
                    ]
                )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
