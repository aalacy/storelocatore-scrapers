import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("bmw_co_uk")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    addresses = []
    max_results = 100
    max_distance = 20
    base_url = "https://www.bmw.co.uk/"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )
    for lat, lng in search:
        logger.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        json_data = session.get(
            "https://discover.bmw.co.uk/proxy/api/dealers?q="
            + str(lat)
            + ","
            + str(lng)
            + "&type=new"
        ).json()

        for data in json_data:
            if "message" in data:
                continue

            location_name = data["dealer_name"]
            street_address = ""

            if data["address_line_1"]:
                street_address += data["address_line_1"]
            if data["address_line_2"]:
                street_address += " " + data["address_line_2"]
            if data["address_line_3"]:
                street_address += " " + data["address_line_3"]

            street_address = (
                street_address.replace("Way Citadel Trading Park", "")
                .replace("Gunnels Wood Road Arlington", "Arlington")
                .strip()
            )
            city = data["town"]
            state = data["county"]
            zipp = data["postcode"]
            country_code = data["country"]
            store_number = data["id"]
            phone = data["primary_phone"]
            location_type = "<MISSING>"
            latitude = data["latitude"]
            longitude = data["longitude"]
            page_url = data["url"]

            if page_url:

                if (
                    page_url == "https://www.buchananbmw.co.uk"
                    or page_url == "https://www.ridgewaysalisburybmw.co.uk"
                    or page_url == "https://www.bmwparklane.com"
                ):
                    hours = "<MISSING>"
                else:
                    try:
                        soup = BeautifulSoup(
                            session.get(
                                page_url + "/contact-us/", headers=headers
                            ).text,
                            "lxml",
                        )
                        try:
                            hours = (
                                " ".join(
                                    list(
                                        soup.find(
                                            "section", {"class": "opening-hours"}
                                        ).stripped_strings
                                    )
                                )
                                .replace("Opening Hours", "")
                                .strip()
                            )
                        except:
                            hours = (
                                " ".join(
                                    list(
                                        soup.find(
                                            class_="openingTimes"
                                        ).stripped_strings
                                    )
                                )
                                .replace("Opening Hours", "")
                                .strip()
                            )
                    except:
                        try:
                            soup = BeautifulSoup(
                                session.get(
                                    session.get(
                                        page_url + "/contact-us/", headers=headers
                                    ).url
                                    + "/contact-us/"
                                ).text,
                                "lxml",
                            )
                            hours = (
                                " ".join(
                                    list(
                                        soup.find(
                                            "section", {"class": "opening-hours"}
                                        ).stripped_strings
                                    )
                                )
                                .replace("Opening Hours", "")
                                .strip()
                            )
                        except:
                            hours = "<MISSING>"
            else:
                hours = "<MISSING>"

            search.found_location_at(latitude, longitude)

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(re.sub(r"\s+", " ", street_address).strip())
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)

            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
