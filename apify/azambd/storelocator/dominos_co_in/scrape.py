import re
from lxml import html
import time
from concurrent.futures import ThreadPoolExecutor

from sgpostal.sgpostal import parse_address_intl
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from tenacity import retry, stop_after_attempt
import tenacity


website = "https://www.dominos.co.in"
MISSING = SgRecord.MISSING
max_workers = 1

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(10))
def request_with_retries(url, retry=1):
    try:
        with SgRequests(proxy_country="in") as http:
            return (http.get(url, headers=headers)).text, url
    except Exception:
        if retry > 10:
            log.error(f"Error loading {url}")
            return None, url
        return request_with_retries(url, retry + 1)


def fetch_stores():
    response, rr = request_with_retries(f"{website}/sitemap")
    body = html.fromstring(response, "lxml")
    states = body.xpath('//a[contains(@href, "/sitemap/")]/@href')
    log.info(f"Total states = {len(states)}")

    count = 0
    page_urls = []
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, rr in executor.map(request_with_retries, states):
            count = count + 1
            try:
                if response is None:
                    continue
                body = html.fromstring(response, "lxml")
                urls = body.xpath('//div[contains(@class, "disclaimer")]/ul/li/a/@href')
                for page_url in urls[1:]:
                    if page_url in page_urls:
                        continue
                    page_urls.append(page_url)
                if count % 30 == 0:
                    log.info(f"{count}. total stores = {len(page_urls)}")
            except Exception as e:
                log.info(f"Err in threadPool: {e}")
                pass
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
        log.info(f"Err in address: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def split_text(text, variable):
    try:
        val = text.split(variable + '":')[1].splitlines()[0].replace(",", "")
        return val
    except Exception as e:
        log.info(f"Err in spliting text: {e}")
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
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    count = 0

    location_type = MISSING
    store_number = MISSING
    country_code = "IN"

    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for response, page_url in executor.map(request_with_retries, stores):
            count = count + 1
            try:
                log.debug(f"{count}. fetching {page_url} ...")
                if response is None:
                    continue
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
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
