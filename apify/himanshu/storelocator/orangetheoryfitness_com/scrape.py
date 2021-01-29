import csv
from sgrequests import SgRequests
import re

session = SgRequests()
import requests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    base_url = "https://www.orangetheory.com"
    for country_url in [
        "https://www.orangetheory.com/bin/otf/getStudioPagesDetail.en_ca.json",
        "https://www.orangetheory.com/bin/otf/getStudioPagesDetail.en_us.json",
    ]:
        json_data = requests.get(country_url).json()["data"]
        for data in json_data:
            if "https" in data["studioURL"]:
                page_url = data["studioURL"]
            else:
                page_url = base_url + data["studioURL"]
            store_number = data["studioID"]
            location_data = requests.get(
                "https://api.orangetheory.co/partners/studios/v2?latitude=&longitude=&distance=&country=&studioId="
                + str(store_number)
            ).json()
            try:
                for loc in location_data["data"][0]:
                    location_name = loc["studioName"]
                    street_address = re.sub(
                        r"\s+", " ", loc["studioLocation"]["physicalAddress"]
                    )
                    city = loc["studioLocation"]["physicalCity"]
                    state = loc["studioLocation"]["physicalState"]
                    zipp = loc["studioLocation"]["physicalPostalCode"]
                    country_code = (
                        loc["studioLocation"]["physicalCountry"]
                        .replace("Canada", "CA")
                        .replace("United States", "US")
                    )
                    if loc["studioLocation"]["phoneNumber"]:
                        phone = loc["studioLocation"]["phoneNumber"].replace(".", "")
                    else:
                        phone = "<MISSING>"
                    latitude = loc["studioLocation"]["latitude"]
                    longitude = loc["studioLocation"]["longitude"]
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
                    store.append("<MISSING>")
                    store.append(latitude)
                    store.append(longitude)
                    store.append("<MISSING>")
                    store.append(page_url)
                    store = [str(x).strip() if x else "MISSING" for x in store]
                    if "8765-e-orchid-rd-704" not in page_url:
                        yield store
            except:
                pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
