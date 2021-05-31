import csv
import json
import lxml.html
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape import sgpostal as parser
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("circlek_com")


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
        "lat": 35.7796,
        "lng": -78.6382,
        "distance": 50000,
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


def fetch_details(store, session):
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

    try:
        store_req = session.get(page_url, headers=headers)
    except:
        return

    store_sel = lxml.html.fromstring(store_req.text)
    json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
    for js in json_list:
        if "LocalBusiness" in js:
            store_json = json.loads(js)
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
    tracker = []

    with ThreadPoolExecutor() as executor, SgRequests() as session:
        locations = fetch_locations(tracker, session)
        futures = [
            executor.submit(fetch_details, location, session) for location in locations
        ]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
