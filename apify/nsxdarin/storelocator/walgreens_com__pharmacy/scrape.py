import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.static import static_zipcode_list, SearchableCountries
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("walgreens_com__pharmacy")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for rows in data:
            writer.writerows(rows)


search = static_zipcode_list(10, SearchableCountries.USA)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "content-type": "application/json; charset=UTF-8",
}


def fetch_locations(code, ids):
    logger.info(("Pulling Postal Code %s..." % code))
    url = "https://www.walgreens.com/locator/v1/stores/search?requestor=search"
    payload = {
        "r": "50",
        "requestType": "dotcom",
        "s": "20",
        "p": 1,
        "q": code,
        "lat": "",
        "lng": "",
        "zip": code,
    }
    data = session.post(url, headers=headers, data=json.dumps(payload)).json()
    website = "walgreens.com/pharmacy"

    locations = []
    if not data.get("results"):
        return locations

    for item in data["results"]:
        store = item["storeSeoUrl"].split("/id=")[1]
        if store in ids:
            continue
        ids.append(store)

        loc = "https://www.walgreens.com" + item["storeSeoUrl"]
        lat = item["latitude"]
        country = "US"
        lng = item["longitude"]
        add = item["store"]["address"]["street"]
        zc = item["store"]["address"]["zip"]
        city = item["store"]["address"]["city"]
        state = item["store"]["address"]["state"]
        name = item["store"]["name"]
        phone = (
            item["store"]["phone"]["areaCode"].strip()
            + item["store"]["phone"]["number"].strip()
        )
        hours = ""
        typ = "<MISSING>"

        page = session.get(loc, headers=headers).text
        soup = BeautifulSoup(page, "html.parser")

        try:
            data = json.loads(soup.select_one("#jsonLD").string)
            hours = data["openingHoursSpecification"]

            hours_of_operation = []
            for hour in hours:
                day = hour["dayOfWeek"].split(" ").pop(0)
                opens = hour["opens"]
                closes = hour["closes"]

                hours_of_operation.append(f"{day}: {opens}-{closes}")
        except:
            hours = "<MISSING>"

        locations.append(
            [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                (",").join(hours_of_operation),
            ]
        )

    return locations


def fetch_data():
    ids = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_locations, code, ids) for code in search]
        for future in as_completed(futures):
            locations = future.result()
            yield locations


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
