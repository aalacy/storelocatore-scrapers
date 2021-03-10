import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests


logger = SgLogSetup().get_logger("hibbett_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    stores = []

    location_url = "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/default/Stores-GetNearestStores?latitude=40.7377313&longitude=-73.6131232&countryCode=US&distanceUnit=mi&maxdistance=5000"

    req = session.get(location_url, headers=headers)
    base = BeautifulSoup(req.text, "lxml")
    if "page has been denied" in str(base):
        logger.info("BLOCKED BY WEBSITE")
    else:
        stores = json.loads(base.text.strip())["stores"].items()
        logger.info("Stores found!!")

    data = []
    locator_domain = "hibbett.com"
    for store in stores:
        store = store[1]

        if store["isOpeningSoon"]:
            continue

        # Store ID
        location_id = store["id"]

        # Name
        location_title = store["name"]

        # Type
        location_type = "<MISSING>"

        # Street
        street_address = (
            (store["address1"] + " " + store["address2"]).replace("  ", " ").strip()
        )

        # State
        state = store["stateCode"]

        # city
        city = store["city"]

        # zip
        zipcode = store["postalCode"]

        # Lat
        lat = store["latitude"]

        # Long
        lon = store["longitude"]

        # Phone
        phone = store["phone"]
        if not phone:
            phone = "<MISSING>"

        # Hour
        hour = store["storeHours"].replace("\n", " ").strip()

        # Country
        country = store["countryCode"]

        link = (
            "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/default/Stores-Details?StoreID="
            + location_id
        )

        # Store data
        data.append(
            [
                locator_domain,
                link,
                location_title,
                street_address,
                city,
                state,
                zipcode,
                country,
                location_id,
                phone,
                location_type,
                lat,
                lon,
                hour,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
