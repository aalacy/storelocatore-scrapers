import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("cmxcinemas.com")


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

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "cmxcinemas.com"

    base_link = "https://www.cmxcinemas.com/location"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    states = list(base.find(id="drpStateloc").stripped_strings)[1:]
    all_store_data = []

    api_link = "https://www.cmxcinemas.com/Locations/FilterLocations?state="

    for st in states:
        stores = session.get(api_link + st, headers=headers).json()["listloc"][0][
            "city"
        ]
        logger.info(st)

        for store in stores:

            link = "https://www.cmxcinemas.com/Locationdetail/" + store["slugname"]
            logger.info(link)

            location_name = store["cinemaname"]
            street_address = store["address"].split(", MN")[0].strip()
            city = store["locCity"].replace("MN", "").strip()
            state = st
            zip_code = store["postalcode"].replace("21075", "20175")
            country_code = "US"

            store_number = "<MISSING>"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
            location_type = "<MISSING>"

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                map_link = base.iframe["src"]
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[
                    lat_pos + 3 : map_link.find("!", lat_pos + 5)
                ].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[
                    lng_pos + 3 : map_link.find("!", lng_pos + 5)
                ].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            all_store_data.append(
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

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
