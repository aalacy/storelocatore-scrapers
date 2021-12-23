from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from lxml import html
import cloudscraper
import os
from tenacity import retry, stop_after_attempt
import tenacity
import json
import ssl
import time
import random
from sgpostal.sgpostal import parse_address_intl
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


LOCATION_URL = "https://www.1800packrat.com/locations"
DOMAIN = "1800packrat.com"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger(logger_name="1800packrat_com")
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


proxy_password = os.environ["PROXY_PASSWORD"]
DEFAULT_PROXY_URL = (
    f"http://groups-RESIDENTIAL,country-us:{proxy_password}@proxy.apify.com:8000/"
)
proxies = {
    "http": DEFAULT_PROXY_URL,
    "https": DEFAULT_PROXY_URL,
}  # Proxy that works with cloudscraper


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def get_store_urls(url):
    try:
        scraper = cloudscraper.CloudScraper()
        response = scraper.get(url, proxies=proxies, headers=headers)
        logger.info(f"{LOCATION_URL} >> HTTP Status Code: {response.status_code}")
        geo = dict()
        urls = []
        urls_latlng = []
        tree = html.fromstring(response.text, "lxml")
        text = (
            "".join(tree.xpath("//script[contains(text(), 'markers:')]/text()"))
            .split("markers:")[1]
            .split("]")[0]
            .strip()[:-1]
            + "]"
        )
        js = json.loads(text)
        for j in js:
            slug = j.get("Link")
            url = f"https://www.{DOMAIN}{slug}"
            urls.append(url)
            lat = j.get("Latitude") or MISSING
            lng = j.get("Longitude") or MISSING
            geo[slug] = {"lat": lat, "lng": lng}
            logger.info(f"Latitude & Longitude: {geo}")
            logger.info(f"List of Store URLs: {urls}")

        for k, v in geo.items():
            url = f"https://www.1800packrat.com{k}"
            lat = v["lat"]
            lng = v["lng"]
            z = (url, lat, lng)
            urls_latlng.append(z)

        return urls_latlng

    except Exception as e:
        logger.info(f" {e} >> Error getting from {LOCATION_URL}")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(url):
    scraper = cloudscraper.CloudScraper()
    response_proxy = scraper.get(url, proxies=proxies)
    time.sleep(random.randint(5, 10))
    page_sel = html.fromstring(response_proxy.text, "lxml")
    a = page_sel.xpath('//div[@class="location-info"]/div//text()')
    a1 = "".join(a)
    if response_proxy.status_code == 200 and "CUSTOMER SERVICE HOURS" in a1:
        logger.info(f"[ {url} ] | Address Data: {a1}")
        logger.info(f"{url} >> HTTP Status: {response_proxy.status_code}")
        return response_proxy

    raise Exception(f"{url} >> Temporary Error: {response_proxy.status_code}")


def fetch_record(idx, url_latlng, sgw: SgWriter):
    store_url = url_latlng[0]
    response = get_response(store_url)
    time.sleep(random.randint(5, 7))
    logger.info(f"Pulling the data from {store_url}")
    page_sel = html.fromstring(response.text, "lxml")

    location_name = "".join(page_sel.xpath("//title/text()"))
    location_name = (
        location_name.split("|")[-1]
        + ", "
        + location_name.split("|")[0].split(" in ")[-1]
    )
    location_name = location_name.strip() or MISSING
    if (
        "1800-PACK-RAT, Portable Storage & Mobile Moving Containers Houston, TX"
        in location_name
    ):
        location_name = "1800-PACK-RAT, Houston, TX"
    logger.info(f"[{idx}] locname: {location_name}")

    page_url = store_url
    a = page_sel.xpath('//div[@class="location-info"]/div//text()')
    b = [" ".join(i.split()) for i in a]
    c = [i for i in b if i]
    d = None
    if "Storage facility access available by appointment" in c:
        d = c[:-1]
    else:
        d = c
    add = ", ".join(d)
    add1 = add.split("CUSTOMER SERVICE HOURS")
    add2 = add1[0].split(",")
    add3 = [i.strip() for i in add2]
    add4 = [i for i in add3 if i]
    add5 = add4[:-1]
    address_x = ", ".join(add5)
    pai = parse_address_intl(address_x)
    sta1 = pai.street_address_1
    sta2 = pai.street_address_2
    street_address = ""
    if sta1 is not None and sta2 is None:
        street_address = sta1
    elif sta1 is not None and sta2 is not None:
        street_address = sta1 + ", " + sta2
    else:
        street_address = MISSING

    city = pai.city or MISSING
    state = pai.state or MISSING
    zip_postal = pai.postcode or MISSING
    country_code = "US"
    store_number = MISSING

    phone = "".join(add4[-1:])
    phone = phone if phone else MISSING
    logger.info(f"[{idx}] Phone: {phone}")

    location_type = "MovingCompany"

    lat = url_latlng[1] or MISSING
    latitude = lat
    logger.info(f"[{idx}] Latitude: {lat}")

    lng = url_latlng[2] or MISSING
    longitude = lng
    logger.info(f"[{idx}] Longitude: {lng}")

    locator_domain = "1800packrat.com"

    hoo_raw = ", ".join(d)
    hoo_raw1 = hoo_raw.split("CUSTOMER SERVICE HOURS")
    hours_of_operation = hoo_raw1[-1].lstrip(",").strip()
    hours_of_operation = hours_of_operation if hours_of_operation else MISSING
    logger.info(f"[{idx}] HOO: {hours_of_operation}")
    raw_address = address_x
    raw_address = raw_address if raw_address else MISSING
    row = SgRecord(
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

    sgw.write_row(row)


def scrape(sgw: SgWriter):
    urls_latlng = get_store_urls(LOCATION_URL)
    with ThreadPoolExecutor(max_workers=6) as executor:
        task = {
            executor.submit(fetch_record, idx, url_latlng, sgw): url_latlng
            for idx, url_latlng in enumerate(urls_latlng[0:])
        }
        for future in as_completed(task):
            future.result()


if __name__ == "__main__":
    logger.info("Started")
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        scrape(writer)
    logger.info("Finished")
