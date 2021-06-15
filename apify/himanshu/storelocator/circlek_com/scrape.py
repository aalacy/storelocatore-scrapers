import csv
import json
import threading
import lxml.html
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape import sgpostal as parser
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import Retrying, stop_after_attempt
from time import sleep
from random import randint

logger = SgLogSetup().get_logger("circlek_com")

local = threading.local()


def get_session(reset):
    if not hasattr(local, "session") or local.count > 5 or reset:
        local.session = SgRequests()
        local.count = 0

    local.count += 1
    sleep(randint(2, 5))
    return local.session


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


headers = {
    "authority": "www.circlek.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_page(page, session):
    url = "https://www.circlek.com/stores_new.php"
    params = {
        "lat": 43.5890,
        "lng": -79.6441,
        "distance": 5000,
        "services": "",
        "region": "global",
        "page": page,
    }
    response = session.get(url, headers=headers, params=params)
    try:
        data = response.json()["stores"]
        stores = data.items() if isinstance(data, dict) else data
        return stores
    except Exception as e:
        logger.error(f"failure to fetch {response.url} >>> {e}")
        return []


def fetch_locations(tracker, session, locations=[], page=0):
    stores = fetch_page(page, session)
    for id, store in stores:
        if id in tracker or store["country"].upper() not in ["US", "CA", "CANADA"]:
            continue
        tracker.append(id)
        locations.append(store)
    if len(stores):
        return fetch_locations(tracker, session, locations, page + 1)
    else:
        return locations


retryer = Retrying(stop=stop_after_attempt(3), reraise=True)


def fetch_details(store, retry=False):
    locator_domain = "https://www.circlek.com"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = "https://www.circlek.com" + store["url"]

    with get_session(retry) as session:
        store_req = session.get(
            page_url,
            headers=headers,
        )

    if store_req.status_code not in (500, 404, 200):
        return retryer(fetch_details, store, True)

    store_sel = lxml.html.fromstring(store_req.text)
    json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
    for js in json_list:
        if "LocalBusiness" in js:
            try:
                store_json = json.loads(js)
            except:
                return retryer(fetch_details, store, True)
            location_name = (
                store.get("display_brand")
                or store.get("store_brand")
                or store.get("name")
                or "<MISSING>"
            )
            if store["franchise"] == "1":
                location_type = "Brand Store"
            else:
                location_type = "Dealer/Distributor/Retail Partner"

            phone = store_json["telephone"]
            street_address = (
                store_json["address"]["streetAddress"]
                .replace("  ", " ")
                .replace("r&#039;", "'")
                .replace("&amp;", "&")
                .strip()
            )
            if street_address[-1:] == ",":
                street_address = street_address[:-1]
            city = store_json["address"]["addressLocality"].strip()

            state = ""
            zipp = store_json["address"]["postalCode"].strip()
            country_code = store["country"]
            latitude = store_json["geo"]["latitude"]
            longitude = store_json["geo"]["longitude"]
            store_number = store["cost_center"]
            raw_address = store_json["name"]
            formatted_addr = parser.parse_address_intl(raw_address)
            state = formatted_addr.state
            hours = store_sel.xpath(
                '//div[@class="columns large-12 middle hours-wrapper"]/div[contains(@class,"hours-item")]'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                time = "".join(hour.xpath("span[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zipp == "" or zipp is None:
                zipp = "<MISSING>"

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"

            if phone == "" or phone is None:
                phone = "<MISSING>"

            if (
                street_address == "<MISSING>"
                and city == "<MISSING>"
                and state == "<MISSING>"
            ):
                return retryer(fetch_details, store, True)

            return [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]


def fetch_data():
    with ThreadPoolExecutor() as executor, SgRequests() as session:
        tracker = []
        locations = fetch_locations(tracker, session)

        futures = [executor.submit(fetch_details, location) for location in locations]
        for future in as_completed(futures):
            poi = future.result()

            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
