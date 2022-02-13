from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import json
from concurrent.futures import ThreadPoolExecutor

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.aldi.com.au/en"
page_url = "https://storelocator.aldi.com.au/Presentation/AldiSued/en-au/Start"
stores_url = "https://www.yellowmap.de/Presentation/AldiSued/en-AU/ResultList?Lux={}&Luy={}&Rlx={}&Rly={}"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
logger = sglog.SgLogSetup().get_logger(logger_name=website)

DIVISION = 240


def fetch_stores(co_ord, retry=1):
    x1, x2, y1, y2 = co_ord
    try:
        response = session.get(stores_url.format(x1, y1, x2, y2), headers=headers)
        response = json.loads(response.text)
        container = response["Container"]
        if container is None:
            return []
        try:
            body = html.fromstring(container, "lxml")
            data = body.xpath('//li[contains(@class, "resultItem clearfix")]')
        except Exception:
            if retry < 4:
                return fetch_stores(co_ord, retry + 1)
            return []
    except Exception:
        if retry < 4:
            return fetch_stores(co_ord, retry + 1)
        return []

    stores = []
    for singleData in data:
        dataJson = json.loads(singleData.xpath(".//@data-json")[0])
        store = {
            "store_number": dataJson["id"],
            "latitude": dataJson["locY"],
            "longitude": dataJson["locX"],
            "location_name": stringify_children(
                singleData, './/div[contains(@class, "shopInfos")]'
            ),
            "raw_address": stringify_children(singleData, ".//address"),
            "hoo": stringify_children(
                singleData, './/table[contains(@class, "openingHoursTable")]'
            ),
        }
        stores.append(store)

    return stores


def stringify_children(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_all_co_ordinates():
    x1 = 112.01
    x2 = 155.01

    y1 = -23.01
    y2 = -39.01

    diffX = (x2 - x1) / DIVISION
    diffY = (y1 - y2) / DIVISION
    xs = []
    ys = []

    for index in range(DIVISION + 1):
        xs.append(x1 + index * diffX)
        ys.append(y1 - index * diffY)

    co_ordinates = []

    x1 = xs[0]
    for x in xs[1:]:
        x2 = x
        y1 = ys[0]
        for y in ys[1:]:
            y2 = y
            co_ordinates.append((x1, x2, y1, y2))
            y1 = y2

        x1 = x2
    return co_ordinates


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        logger.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    co_ordinates = get_all_co_ordinates()
    logger.debug(f"Total co_ordinates={len(co_ordinates)}")

    country_code = "AU"
    phone = MISSING
    location_type = MISSING
    count = 0

    with ThreadPoolExecutor(max_workers=24, thread_name_prefix="fetcher") as executor:
        for stores in executor.map(fetch_stores, co_ordinates):
            count = count + 1
            logger.debug(f"{count}. stores = {len(stores)}")

            for store in stores:
                store_number = store["store_number"]
                location_name = store["location_name"]
                latitude = store["latitude"]
                longitude = store["longitude"]
                hours_of_operation = store["hoo"]
                raw_address = store["raw_address"]
                street_address, city, state, zip_postal = get_address(raw_address)

                yield SgRecord(
                    locator_domain="aldi.com.au",
                    store_number=store_number,
                    page_url=page_url,
                    location_name=location_name,
                    location_type=location_type,
                    street_address=street_address,
                    city=city,
                    zip_postal=zip_postal,
                    state=state,
                    country_code=country_code,
                    phone=phone,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )


def scrape():
    logger.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    logger.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
