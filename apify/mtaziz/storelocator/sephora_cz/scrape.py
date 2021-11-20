from urllib.parse import urlparse
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
import json
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "sephora.cz"
LOCATION_URLS_GRID = [
    "https://www.sephora.cz/prodejny",
    "https://www.sephora.dk/butikker/",
    "https://www.sephora.fr/magasin",
    "https://www.sephora.pt/lojas",
    "https://www.sephora.es/tiendas",
    "https://www.sephora.se/butiker/",
    "https://ch.sephora.fr/ch/fr/magasin",
    "https://www.sephora.ae/en/store",
    "https://www.sephora.de/Stores-Alle",
    "https://www.sephora.it/beauty-store/",
    "https://www.sephora.pl/perfumerie",
]

MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("sephora_cz")
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}
MAX_WORKERS = 10


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_store_urls():
    store_urls = []
    for gunum, gurl in enumerate(LOCATION_URLS_GRID[0:]):
        r = get_response(gurl)
        sel = html.fromstring(r.text, "lxml")
        purls = sel.xpath('//a[contains(@class, "store-name")]/@href')
        logger.info(f"Pulling the store URLs from: {gurl}")
        logger.info(f"{gurl} | Total number of Store URLs: {len(purls)}")
        store_urls.extend(purls)
    return store_urls


def fetch_records(idx, store_url, sgw: SgWriter):
    logger.info(f"[{idx}] Pulling the data from: {store_url}")
    rcz = get_response(store_url)
    sel_cz = html.fromstring(rcz.text, "lxml")
    dcz = sel_cz.xpath(
        '//script[contains(@type, "application/ld+json") and contains(text(), "telephone")]/text()'
    )
    dcz1 = "".join(dcz)
    data_json = json.loads(dcz1)
    domain = urlparse(store_url).netloc
    locator_domain = domain.replace("www.", "")
    page_url = store_url
    logger.info(f"[{idx}] page_url: {page_url}")

    location_name = data_json["name"]
    location_name = location_name if location_name else MISSING
    logger.info(f"[{idx}] location_name: {location_name}")

    add = data_json["address"]
    street_address = add["streetAddress"]
    logger.info(f"[{idx}] Street Address: {street_address}")

    city = add["addressLocality"]
    city = city if city else MISSING
    logger.info(f"[{idx}] City: {city}")

    state = ""
    state = state if state else MISSING
    logger.info(f"[{idx}] State: {state}")

    zip_postal = add["postalCode"]
    zip_postal = zip_postal if zip_postal else MISSING
    logger.info(f"[{idx}] Zip Code: {zip_postal}")

    country_code = locator_domain.split(".")[-1].upper()
    logger.info(f"[{idx}] country_code: {country_code}")

    store_number = page_url.split("storeID=")[-1]
    logger.info(f"[{idx}] store_number: {store_number}")

    phone = data_json["telephone"]
    phone = phone if phone else MISSING
    logger.info(f"[{idx}] Phone: {phone}")

    # Location Type
    location_type = data_json["@type"]
    location_type = location_type if location_type else MISSING
    logger.info(f"[{idx}] location_type: {location_type}")

    # Latlng
    latlng = "".join(
        sel_cz.xpath(
            '//div[contains(@data-default-coordinates, "longitude")]/@data-coord'
        )
    )
    latlng1 = json.loads(latlng)

    # Latitude
    latitude = latlng1["lat"]
    latitude = latitude if latitude else MISSING
    logger.info(f"[{idx}] lat: {latitude}")

    # Longitude
    longitude = latlng1["lng"]
    longitude = longitude if longitude else MISSING
    logger.info(f"[{idx}] lng: {longitude}")

    hours_of_operation = ""
    hoo = data_json["openingHours"]
    if isinstance(hoo, list):
        hours_of_operation = ", ".join(hoo)
    else:
        hours_of_operation = hoo

    logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

    # Raw Address
    raw_address = ""
    raw_address = raw_address if raw_address else MISSING
    idx += 1
    item = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=country_code,
        store_number=store_number,
        phone=phone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )
    sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    page_urls = get_store_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, idx, store_url, sgw)
            for idx, store_url in enumerate(page_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
