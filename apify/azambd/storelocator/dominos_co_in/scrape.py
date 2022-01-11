import re
import json
import time
from lxml import html
from concurrent.futures import ThreadPoolExecutor

from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "https://www.dominos.co.in"
sitemap_url = f"{website}/store-location-pages.xml"
MISSING = SgRecord.MISSING
max_workers = 12

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url, retry=1):
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 404:
            return -1, url
        if response.status_code != 200:
            log.error(f"{url} ::: {response.status_code}")
            return request_with_retries(url, retry + 1)
        return response.text, url
    except Exception as e:
        log.debug(f"failed loading: {url} with Error: {e}")
        if retry > 4:
            return None, url
        return request_with_retries(url, retry + 1)


def fetch_stores():
    response, url = request_with_retries(f"{website}/store-locations")
    if response is None:
        return []
    body = html.fromstring(response, "lxml")
    response = body.xpath('//meta[contains(@name, "advance-search")]/@content')[0]
    states = []
    for data in json.loads(response):
        states.append(f"{website}/store-locations/api/get-cities/{data['id']}")
    log.debug(f"Total states = {len(states)}")

    cities = []
    count = 0
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, url in executor.map(request_with_retries, states):
            count = count + 1
            if response is None or response == "":
                log.error(f"{count}. failed loading url {url}")
                continue
            all_data = json.loads(response)["data"]
            if all_data is None or all_data == "":
                continue
            for data in all_data:
                cities.append(
                    f"{website}/store-locations/api/get-localities/{data['id']}"
                )
            log.debug(f"{count}. cities {len(cities)}")
    log.debug(f"Total cities = {len(cities)}")

    locations = []
    count = 0
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="fetcher") as executor:
        for response, url in executor.map(request_with_retries, cities):
            count = count + 1
            if response is None or response == "":
                log.error(f"{count}. failed loading url {url}")
                continue
            all_data = json.loads(response)["data"]
            if all_data is None or all_data == "":
                continue
            for data in all_data:
                locations.append(
                    f"{website}/store-locations/pizza-delivery-food-restaurants-in-{data['link']}"
                )
            log.debug(f"{count}. locations {len(locations)}")
    log.debug(f"Total locations {len(locations)}")

    page_urls = []
    count = 0
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, url in executor.map(request_with_retries, locations):
            count = count + 1
            if response is None or response == "":
                log.error(f"{count}. failed loading url {url}")
                continue
            try:
                body = html.fromstring(response, "lxml")
                urls = body.xpath("//h3/a/@href")
                for url in urls:
                    if url not in page_urls:
                        page_urls.append(url)
            except Exception as e:
                log.error(f"{count}. failed loading url {url}: {e}")
            if count % 1000 == 0:
                log.debug(f"{count} page_urls {len(page_urls)}")

    log.debug(f"Total page_urls {len(page_urls)}")
    return page_urls


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
        log.debug(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def split_text(text, variable):
    try:
        val = text.split(variable + '":')[1].splitlines()[0].replace(",", "")
        return val
    except Exception as e:
        log.debug(f"Split Error: {e}")
        return MISSING


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def get_ra(address):
    if len(address) == 0:
        return MISSING
    address = address[0]
    address = address.split(", PH.NO.")[0].strip()
    address = address.split("PH.NO.")[0].strip()
    if "phone" in address.lower():
        address = address.lower().split("phone")[0].strip().capitalize()
    if "ph." in address.lower():
        address = address.lower().split("ph.")[0].strip().capitalize()
    if "ph-" in address.lower():
        address = address.lower().split("ph-")[0].strip().capitalize()
    if "ph " in address.lower():
        address = address.lower().split("ph ")[0].strip().capitalize()

    address = " ".join(address.rsplit("-", 1))
    phone = get_phone(address)
    address = address.replace(phone, "  ").strip()
    address = address.replace(",,", ",").replace(",", ", ").strip()
    return " ".join(address.split())


def fetch_data():
    page_urls = fetch_stores()
    log.info(f"Total stores = {len(page_urls)}")
    count = 0

    location_type = MISSING
    store_number = MISSING
    country_code = "IN"

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, page_url in executor.map(request_with_retries, page_urls):
            count = count + 1
            try:
                if response is None:
                    log.debug(f"{count}. Failed loading {page_url} ...")
                    continue

                if response == -1:
                    log.debug(f"{count}. 404: Not found {page_url} ...")
                    continue
                log.debug(f"{count}. fetching {page_url} ...")
                body = html.fromstring(response, "lxml")

                location_name = body.xpath("//h1/text()")[0].strip()
                raw_address = get_ra(
                    body.xpath('//h2[contains(@class, "store-page-address")]/text()')
                )
                street_address, city, state, zip_postal = get_address(raw_address)
                latitude = split_text(response, "latitude")
                longitude = split_text(response, "longitude")
                phone = body.xpath('//a[contains(@href, "tel:")]/p/text()')
                if len(phone) > 0:
                    phone = phone[0]
                else:
                    phone = MISSING

                hours_of_operation = body.xpath(
                    '//p[contains(@class, "fontsize4 bold")]/text()'
                )
                if len(hours_of_operation) > 0:
                    hours_of_operation = hours_of_operation[0]
                else:
                    hours_of_operation = MISSING
                if location_name == MISSING or raw_address == MISSING:
                    continue

                yield SgRecord(
                    locator_domain="dominos.co.in",
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
            except Exception as e:
                log.info(f"Err in fetching data: {e}")
                pass
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    CrawlStateSingleton.get_instance().save(override=True)
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
