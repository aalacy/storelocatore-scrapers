import json
import threading
import lxml.html
from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests, SgRequestError
from sgpostal.sgpostal import parse_address_intl
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import Retrying, stop_after_attempt
from time import sleep
from typing import List
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
    logger.info(f"{url} page={page}")
    try:
        response = SgRequests.raise_on_err(
            session.get(url, headers=headers, params=params)
        )
        data = response.json()["stores"]
        stores = data.items() if isinstance(data, dict) else data
        return stores
    except SgRequestError as e:
        logger.error(f"failure to fetch data >>> {e.status_code}")
        return []


def fetch_locations(tracker, session, locations=[], page=0):
    stores = fetch_page(page, session)
    for id, store in stores:
        if id in tracker:
            continue
        tracker.append(id)
        locations.append(store)
    if len(stores) == 0:
        logger.info(f"last page was {page}")
        return locations
    else:
        return fetch_locations(tracker, session, locations, page + 1)


retryer = Retrying(stop=stop_after_attempt(3), reraise=True)


def fetch_details(tup, retry=False):
    store, session = tup
    locator_domain = "https://www.circlek.com"
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = store["cost_center"]
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = "https://www.circlek.com" + store["url"]
    if (
        store["country"].upper() in ["US", "CA", "CANADA"]
        and store["op_status"] != "Planned"
    ):
        logger.info(page_url)
        try:
            store_req = SgRequests.raise_on_err(
                session.get(
                    page_url,
                    headers=headers,
                )
            )

            if store_req.status_code not in (500, 404, 200):
                logger.info(f"Respone invalid {store_req.status_code} - of {page_url}")
                return retryer(fetch_details, (store, get_session(1)), True)

            if '"streetAddress":' not in store_req.text:
                logger.info(f"Respone invalid {store_req.status_code} - of {page_url}")
                return retryer(fetch_details, (store, get_session(1)), True)

            store_sel = lxml.html.fromstring(store_req.text)
            json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
            for js in json_list:
                if "address" in js:
                    try:
                        store_json = json.loads(js)
                    except:
                        continue

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
                                    location_type
                                    + ", "
                                    + raw_type["itemOffered"]["name"]
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
                        store_json["address"]["addressLocality"]
                        .replace("&#039;", "'")
                        .strip()
                    )

                    state = ""
                    zipp = store_json["address"]["postalCode"].strip()
                    country_code = store["country"]
                    latitude = store_json["geo"]["latitude"].replace(",", ".")
                    longitude = store_json["geo"]["longitude"].replace(",", ".")
                    store_number = store["cost_center"]
                    raw_address = (
                        "".join(store_sel.xpath('//h1[@class="heading-big"]//text()'))
                        .strip()
                        .replace("Circle K,", "")
                        .strip()
                        + ","
                        + "".join(
                            store_sel.xpath('//h2[@class="heading-small"]//text()')
                        ).strip()
                    )
                    formatted_addr = parse_address_intl(raw_address)
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
                    break

        except SgRequestError as e:
            logger.error(f"failure >>> {e.status_code}")

        if len(location_name) <= 0:
            street_address = store["address"]
            location_name = "Circle K at " + street_address
            city = store["city"]
            country_code = store["country"]

            latitude = store["latitude"]
            longitude = store["longitude"]

        return [
            locator_domain,
            location_name.replace("Visit your local", "").strip(),
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
        tracker: List[str] = []
        locations = fetch_locations(tracker, session)
        futures = [
            executor.submit(fetch_details, (location, session))
            for location in locations
        ]
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
