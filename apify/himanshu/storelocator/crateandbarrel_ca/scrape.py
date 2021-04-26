import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("crateandbarrel_ca")
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }

    base_url = "https://www.crateandbarrel.ca/"
    location_url = "https://www.crateandbarrel.ca/stores/"
    r = session.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find_all("script")[-1]
    data = (
        "{"
        + str(script).split('"searchKeyword":"",')[1].split(',"storeFilterTypes"')[0]
        + "}"
    )
    json_data = json.loads(data)
    for store in json_data["storeList"]:
        location_name = store["storeName"]
        street_address = store["address1"] + store["address2"]
        city = store["city"]
        state = store["state"]
        if state == "AB":
            state = "Alberta"
        elif state == "ON":
            state = "Ontario"
        elif state == "QC":
            state = "Quebec"
        elif state == "BC":
            state = "British Columbia"

        zipp = store["zip"]
        country_code = "CA"
        store_number = store["storeNumber"]
        phone = (
            store["phoneAreaCode"]
            + "-"
            + store["phonePrefix"]
            + "-"
            + store["phoneSuffix"]
        )
        latitude = store["zipLatitude"]
        longitude = store["zipLongitude"]
        page_url = base_url + store["storeUrl"]
        if store["distributionCenter"] == "True":
            location_type = "Warehouse"
        else:
            location_type = "Store"

        mon = "Mon:" + store["monOpen"] + " - " + store["monClose"]
        tue = "Tue:" + store["tuesOpen"] + " - " + store["tuesClose"]
        wed = "Wed:" + store["wedOpen"] + " - " + store["wedClose"]
        thurs = "Thur:" + store["thursOpen"] + " - " + store["thursClose"]
        fri = "Fri:" + store["friOpen"] + " - " + store["friClose"]
        sat = "Sat:" + store["satOpen"] + " - " + store["satClose"]
        sun = "Sun:" + store["sunOpen"] + " - " + store["sunClose"]
        hours_of_operation = (
            mon
            + " "
            + tue
            + " "
            + wed
            + " "
            + thurs
            + " "
            + fri
            + " "
            + sat
            + " "
            + sun
        )

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
