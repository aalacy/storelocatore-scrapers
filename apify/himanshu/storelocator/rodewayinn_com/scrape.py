from bs4 import BeautifulSoup
import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from datetime import datetime
from datetime import timedelta
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rodewayinn_com")
session = SgRequests()

check_in = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
check_out = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8", newline="") as output_file:
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
    locator_domain = "https://www.choicehotels.com/rodeway-inn"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    addressesess = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=100,
    )

    url = "https://www.choicehotels.com/webapi/location/hotels"

    for lat, long in search:

        payload = (
            "adults=%201&checkInDate=%20"
            + check_in
            + "&checkOutDate=%20"
            + check_out
            + "&lat=%20"
            + str(lat)
            + "&lon=%20"
            + str(long)
            + "&ratePlans=%20RACK%2CPREPD%2CPROMO%2CFENCD&rateType=%20LOW_ALL&searchRadius=100"
        )

        r = session.post(url, headers=headers, data=payload)
        try:
            json_data = r.json()["hotels"]
        except:
            continue

        for addr in json_data:
            if "Rodeway" not in addr["name"]:
                continue
            location_name = addr["name"]
            street_address = addr["address"]["line1"]
            city = addr["address"]["city"]
            state = addr["address"]["subdivision"]
            zipp = addr["address"]["postalCode"]
            country_code = addr["address"]["country"]
            store_number = "<MISSING>"
            phone = addr["phone"]
            location_type = "<MISSING>"
            latitude = addr["lat"]
            longitude = addr["lon"]
            hours_of_operation = "<MISSING>"
            page_url = "https://www.choicehotels.com/" + addr["id"]
            if latitude + longitude in addressesess:
                continue
            addressesess.append(latitude + longitude)

            store = []
            store.append(locator_domain)
            store.append(location_name)
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code)
            store.append(store_number)
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            [
                str(x).strip().replace("\n", "").replace("\t", "").replace("\r", "")
                for x in store
            ]
            req = session.get(page_url, headers=headers)
            soup = BeautifulSoup(req.text, "lxml")
            if soup.find("strong", {"class", "text-uppercase"}):
                continue
            yield store

    r = session.get(
        "https://www.choicehotels.com/webapi/hotels/brand/RW?preferredLocaleCode=en-us&siteName=us",
        headers=headers,
    ).json()
    for value in r["hotels"]:
        store_number = "<MISSING>"
        location_name = value["name"]
        if "line2" in value["address"]:
            street_address = value["address"]["line1"] + " " + value["address"]["line2"]
        else:
            street_address = value["address"]["line1"]
        city = value["address"]["city"]
        state = value["address"]["subdivision"]
        zipp = value["address"]["postalCode"]
        country_code = value["address"]["country"]
        location_type = value["brandName"]
        phone = value["phone"]
        latitude = value["lat"]
        longitude = value["lon"]
        hours_of_operation = "<MISSING>"
        page_url = "https://www.choicehotels.com/" + str(value["id"])
        if latitude + longitude in addressesess:
            continue
        addressesess.append(latitude + longitude)
        store = []
        store.append(locator_domain if locator_domain else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        [
            str(x).strip().replace("\n", "").replace("\t", "").replace("\r", "")
            for x in store
        ]
        req = session.get(page_url, headers=headers)
        soup = BeautifulSoup(req.text, "lxml")
        if soup.find("strong", {"class", "text-uppercase"}):
            continue
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
