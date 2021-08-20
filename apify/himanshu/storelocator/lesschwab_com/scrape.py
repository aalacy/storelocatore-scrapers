import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

session = SgRequests()


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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.lesschwab.com"
    r = session.get(base_url + "/stores/")
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    }
    for atag in soup.find("div", {"class": "footer__container__item"}).find_all("a"):
        url = base_url + atag["href"]
        soup1 = BeautifulSoup(session.get(url, headers=headers).text, "lxml")
        locations = soup1.find_all(
            class_="storeDetails storeDetails--brief js-store-details-brief"
        )
        stores = json.loads(soup1.find(class_="map-canvas")["data-locations"])

        for i in range(len(locations)):
            store = []
            location = locations[i]
            store = stores[i]

            if "soon" in location.find(class_="storeDetails__contact").text.lower():
                continue
            locator_domain = base_url
            link = base_url + location.address.a["href"]
            street_address = (
                location.find(class_="storeDetails__streetName")
                .text.strip()
                .replace("tire shop", "")
                .strip()
            )
            street_address = street_address[street_address.find(".") + 1 :].strip()
            location_name = street_address + " Les Schwab Tire Center"
            city_line = location.address.span.text.strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "Tire Center"
            if "mobile" in street_address.lower():
                location_type = street_address
            try:
                phone = location.find(class_="storeDetails__contact").span.text.strip()
            except:
                phone = "<MISSING>"
            try:
                hours_of_operation = (
                    location.find(class_="storeDetails__information")
                    .div.text.replace("PM", "PM ")
                    .strip()
                )
            except:
                hours_of_operation = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]
            if "mobile" in street_address.lower():
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            return_main_object.append(
                [
                    locator_domain,
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
                    link,
                ]
            )
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
