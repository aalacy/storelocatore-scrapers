import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("kohls_com")

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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }
    domain = "https://www.kohls.com"
    base_url = "https://www.kohls.com/stores.shtml"
    r = session.get(base_url, headers=headers)
    address = []
    soup = BeautifulSoup(r.text, "lxml")
    for state_link in soup.find(id="browse-content").find_all(class_="ga-link"):
        state_url = domain + state_link["href"]
        logger.info(state_url)
        r1 = session.get(state_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        for city_link in soup1.find(id="browse-content").find_all(class_="ga-link"):
            try:
                r2 = session.get(domain + city_link["href"], headers=headers)
            except:
                continue
            soup2 = BeautifulSoup(r2.text, "lxml")
            try:
                for url in soup2.find_all(class_="map-list-item-header"):
                    page_url = domain + url.a["href"]
                    store_number = page_url.split("-")[-1].split(".s")[0]
                    r3 = session.get(page_url, headers=headers)
                    soup3 = BeautifulSoup(r3.text, "lxml")
                    script = soup3.find(
                        "script", attrs={"type": "application/ld+json"}
                    ).contents[0]
                    json_data = json.loads(script)
                    if type(json_data) == list:
                        for l in json_data:
                            location_name = l["name"]
                            location_type = "<MISSING>"
                            latitude = l["geo"]["latitude"]
                            longitude = l["geo"]["longitude"]
                            phone = l["address"]["telephone"]
                            street_address = l["address"]["streetAddress"]
                            city = l["address"]["addressLocality"]
                            state = l["address"]["addressRegion"]
                            zip1 = l["address"]["postalCode"]
                    else:
                        location_name = json_data["name"]
                        latitude = json_data["geo"]["latitude"]
                        longitude = json_data["geo"]["longitude"]
                        location_type = "<MISSING>"
                        phone = json_data["address"]["telephone"]
                        street_address = json_data["address"]["streetAddress"]
                        city = json_data["address"]["addressLocality"]
                        state = json_data["address"]["addressRegion"]
                        zip1 = json_data["address"]["postalCode"]
                    hours = (
                        " ".join(
                            list(soup3.find("div", {"class": "hours"}).stripped_strings)
                        )
                        .replace("\n", "")
                        .replace("ExceptionHours", "")
                        .replace("Exception Hours", "")
                        .strip()
                    )
                    store = []
                    store.append("https://www.kohls.com/")
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zip1)
                    store.append("US")
                    store.append(store_number)
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours)
                    store.append(page_url)
                    if store[2] in address:
                        continue
                    address.append(store[2])
                    yield store
            except:
                continue


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
