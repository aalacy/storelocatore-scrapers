import json
import threading
import lxml.html
from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

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
        "lat": 20.2386,
        "lng": -155.8312,
        "distance": 9999999999,
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
        if store["address"] + store["city"] in tracker:
            continue
        tracker.append(id)
        tracker.append(store["address"] + store["city"])
        locations.append(store)
    try:
        return fetch_locations(tracker, session, locations, page + 1)
    except:
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
                store_json.get("description").split(",")[0]
                or store.get("display_brand")
                or store.get("store_brand")
                or store.get("name")
                or "<MISSING>"
            )
            location_name = (
                location_name.replace("&#039;", "'").replace("amp;", "").strip()
            )

            if location_name == "Circle K at":
                location_name = "Circle K"

            try:
                location_type = ""
                raw_types = store_json["hasOfferCatalog"]["itemListElement"]
                for raw_type in raw_types:
                    if location_type:
                        location_type = (
                            location_type + ", " + raw_type["itemOffered"]["name"]
                        )
                    else:
                        location_type = raw_type["itemOffered"]["name"]

                if not location_type:
                    location_type = "<MISSING>"
            except:
                location_type = "<MISSING>"

            phone = store_json["telephone"]
            street_address = (
                store_json["address"]["streetAddress"]
                .replace("  ", " ")
                .replace("&#039;", "'")
                .replace("&amp;", "&")
                .strip()
            )
            if street_address[-1:] == ",":
                street_address = street_address[:-1]
            city = (
                store_json["address"]["addressLocality"].replace("&#039;", "'").strip()
            )

            state = ""
            zipp = store_json["address"]["postalCode"].strip()
            country_code = store["country"]
            latitude = store_json["geo"]["latitude"].replace(",", ".")
            longitude = store_json["geo"]["longitude"].replace(",", ".")
            store_number = store["cost_center"]
            raw_address = store_json["name"]
            formatted_addr = parser.parse_address_intl(raw_address)
            state = formatted_addr.state
            if state:
                state = state.replace("Mills", "").replace("Est", "").strip()
            if country_code.lower()[:2] == "ca" and state == "CA":
                state = ""
            if state == "ON":
                country_code = "Canada"
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


def fetch_data(sgw: SgWriter):
    with ThreadPoolExecutor() as executor, SgRequests() as session:
        tracker = []  # type: List[str]
        locations = fetch_locations(tracker, session)
        futures = [executor.submit(fetch_details, location) for location in locations]
        for future in as_completed(futures):
            poi = future.result()

            if poi:
                sgw.write_row(
                    SgRecord(
                        locator_domain=poi[0],
                        location_name=poi[1],
                        street_address=poi[2],
                        city=poi[3],
                        state=poi[4],
                        zip_postal=poi[5],
                        country_code=poi[6],
                        store_number=poi[7],
                        phone=poi[8],
                        location_type=poi[9],
                        latitude=poi[10],
                        longitude=poi[11],
                        hours_of_operation=poi[12],
                        page_url=poi[13],
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
