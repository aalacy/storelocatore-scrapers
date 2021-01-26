import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup
import time

logger = SgLogSetup().get_logger("maaco_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    base_url = "https://www.maaco.com"

    r = session.get("https://www.maaco.com/sitemap/")
    soup = BeautifulSoup(r.text, "lxml")

    for st_link in soup.find_all("ul", {"class": "sitemap-sublist"})[1].find_all("a"):
        city_r = session.get(base_url + st_link["href"])
        city_soup = BeautifulSoup(city_r.text, "lxml")
        time.sleep(30)
        for ct_link in city_soup.find_all("a", {"class": "location-cities-list-item"}):

            link = base_url + st_link["href"] + ct_link["href"]
            logger.info(link)
            time.sleep(5)
            r = session.get(link)
            soup = BeautifulSoup(r.text, "lxml")

            for data in soup.find_all(
                "div", {"class": re.compile("locationsearch-storeinfo")}
            ):

                json_data = json.loads(
                    re.sub(
                        r"(\w+):",
                        r'"\1":',
                        (
                            data["data-ng-click"]
                            .replace("gmc.setMapClickHandler(", "")
                            .replace("})", "}")
                            .replace("'", '"')
                        ),
                    )
                )
                location_name = data.find("h2").text.strip()
                street_address = (
                    json_data["streetAddress1"] + " " + str(json_data["streetAddress2"])
                ).strip()
                city = json_data["locationCity"]
                state = json_data["locationState"]
                zipp = json_data["locationPostalCode"]
                store_number = data["data-storeid"]
                phone = json_data["trackingPhone"]
                latitude = json_data["latitude"]
                longitude = json_data["longitude"]
                hours = (
                    " ".join(
                        list(
                            data.find(
                                "div", {"class": "locationsearch-storehours"}
                            ).stripped_strings
                        )
                    )
                    .replace("Store Hours: ", "")
                    .strip()
                )
                page_url = base_url + data.find("h2").find("a")["href"]

                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append("<MISSING>")
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
