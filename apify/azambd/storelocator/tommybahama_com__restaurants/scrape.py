import re
from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import urllib.parse
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.tommybahama.com"
store_url = f"{website}/en/store-finder?q=&searchStores=on&searchOutlets=on&q=&searchRestaurants=on&searchStores=true&searchRestaurants=true&searchOutlets=true&searchInternational=true&page="
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    page = 0
    page_urls = []
    while True:
        response = request_with_retries(f"{store_url}{page}")
        body = html.fromstring(response.text, "lxml")
        urls = body.xpath('//a[contains(text(), "View Store")]/@href')
        if len(urls) == 0:
            break
        for url in urls:
            page_urls.append(f"{website}{urllib.parse.quote(url)}")
        log.debug(f"From {page}: stores = {len(urls)}; total Stores = {len(page_urls)}")
        page = page + 1
    return page_urls


def getJSparams(body, variable):
    try:
        return body.split(f"{variable} = '")[1].split("'")[0]
    except Exception as e:
        log.info(f"Split Error: {e}")
        return MISSING


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
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def stringify_nodes(body, xpath):
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


def get_hoo(hours_of_operation):
    hours_of_operation = (
        hours_of_operation.replace("Hours:", "")
        .replace("Hours", "")
        .replace("ours:", "")
        .strip()
    )
    extras = [
        "This location may",
        "Get Directions",
        "The Gardens",
        "The Shops",
        "Shops",
        ">",
    ]
    for extra in extras:
        if extra in hours_of_operation:
            hours_of_operation = hours_of_operation.split(extra)[0].strip()
    hoo = []
    gg = [
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
        "am",
        "pm",
        "daily",
        "closed",
        "-",
        "open",
    ]
    for h in hours_of_operation.split():
        hs = h.lower()
        fo = hs.isnumeric()
        for g in gg:
            if g in hs:
                fo = True
        if fo is False:
            break
        hoo.append(h)

    if len(hoo) == 0:
        return hours_of_operation
    if hoo[len(hoo) - 1].isnumeric():
        hoo.pop()
    return " ".join(hoo)


def fetch_data():
    page_urls = fetch_stores()
    log.info(f"Total stores = {len(page_urls)}")
    count = 0
    country_code = "US"
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. fetching {page_url} ...")
        location_type = (
            "restaurants and bars"
            if "/restaurants-and-marlin-bars" in page_url
            else "store"
        )
        if location_type == "store":
            continue

        response = request_with_retries(page_url)
        body = html.fromstring(response.text, "lxml")

        if location_type == "store":
            location_name = stringify_nodes(body, "//h1")
            bodyDiv = stringify_nodes(
                body, "//div[contains(@class, 'store-locator-details')]"
            )
            store_number = body.xpath(
                "//meta[@name='store-locator-store-number']/@content"
            )[0]
            street_address, city, state, zip_postal = get_address(bodyDiv)
            phone = get_phone(bodyDiv)
            latitude = getJSparams(response.text, "storelatitude")
            longitude = getJSparams(response.text, "storelongitude")
            hours_of_operation = bodyDiv.split("Store Hours")[1]
        else:

            location_name = body.xpath(
                "//p[@class='location-details-locationName']/text()"
            )[0]
            latitude = MISSING
            longitude = MISSING
            store_number = MISSING
            bodyDiv = stringify_nodes(
                body, "//div[contains(@class, 'restaurant-location-map-details')]"
            )

            street_address, city, state, zip_postal = get_address(bodyDiv)
            phone = get_phone(bodyDiv).split(" ")[0]
            hours_of_operation = bodyDiv.split(phone)[1].split("Live Music:")[0].strip()

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        hours_of_operation = (
            hours_of_operation.replace(raw_address, "").replace("|", ",").strip()
        )
        # off calling get_hoo()
        yield SgRecord(
            locator_domain="tommybahama.com",
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
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
