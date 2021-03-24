import re
import csv
import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hollisterco_com")

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
}


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


@retry(stop=stop_after_attempt(3))
def fetch_locations(base_url, session):
    location_url = f"{base_url}/shop/ViewAllStoresDisplayView?storeId=11205&catalogId=10201&langId=-1"

    session.get(base_url, headers=headers, timeout=20)
    res = session.get(location_url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")
    links = soup.find_all("li", {"class": "view-all-stores__store"})

    return [link.a["href"] for link in links if is_location(link.a["href"])]


def is_location(link):
    return re.search(r"\/clothing-stores\/(CA|US|GB)\/", link, re.I)


@retry(stop=stop_after_attempt(3))
def fetch_location(url, session):

    res = session.get(url, headers=headers, timeout=20)
    if res.status_code == 404:
        return None

    soup = BeautifulSoup(res.text, "lxml")

    return extract_data(soup)


def extract_data(soup):
    scripts = soup.find_all("script")

    for script in scripts:
        if script.string and "geoNodeUniqueId" in script.string:
            data = json.loads(
                script.string.split("try {digitalData.set('physicalStore',")[1].split(
                    ");}"
                )[0]
            )

            return data


def fetch_data():

    base_url = "https://www.hollisterco.com"
    requests = SgRequests()
    links = fetch_locations(base_url, requests)

    for link in links:
        page_url = f"{base_url}{link}"
        data = fetch_location(page_url, requests)
        if not data:
            continue

        location_name = data["name"]
        street_address = data["addressLine"][0]
        city = data["city"]
        state = data["stateOrProvinceName"]
        zipp = data["postalCode"]
        country_code = data["country"]
        store_number = data["storeNumber"]
        phone = data["telephone"]
        location_type = "<MISSING>"
        latitude = data["latitude"]
        longitude = data["longitude"]
        hours_of_operation = "<INACCESSIBLE>"

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
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
