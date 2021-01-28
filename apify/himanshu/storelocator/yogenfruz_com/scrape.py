import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("yogenfruz_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_url = "https://www.yogenfruz.com"
    r = session.get("https://yogenfruz.com/find-a-store/")
    soup = BeautifulSoup(r.text, "lxml")
    addresses = []

    locator_domain = base_url
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "yogen fruz"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    locs = soup.find_all("div", {"class": "location-search-result col-md-4"})
    for loc in locs:
        page_url = loc.find("a", {"class": "location-link"})["href"]
        location_name = loc.find("a", {"class": "location-link"}).text
        street_address = loc.find(
            "div", {"class": "location-detail-address-1"}
        ).text.strip()
        if loc.find("div", {"class": "location-detail-address-3"}):
            city_state_zip = (
                loc.find("div", {"class": "location-detail-address-3"})
                .text.strip()
                .split(",")
            )
            city = city_state_zip[0].strip()
            state = city_state_zip[1].strip()
            zipp = city_state_zip[-1].strip()
        if len(zipp) == 5:
            country_code = "US"
        else:
            country_code = "CA"

        if loc.find("a", {"class": "address-block-phone"}):
            phone = loc.find("a", {"class": "address-block-phone"}).text.strip()

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
