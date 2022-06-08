from sgpostal.sgpostal import parse_address_usa
from lxml import html
import time
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from concurrent import futures
import re

DOMAIN = "homelessshelterdirectory.org"
website = "https://www.homelessshelterdirectory.org"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetch_stores():
    response = request_with_retries(f"{website}")
    body = html.fromstring(response.text, "lxml")
    state_urls = body.xpath(
        '//select[contains(@id, "states_home_search")]/option/@value'
    )
    log.info(f"total states = {len(state_urls)}")

    city_urls = []
    for state_url in state_urls:
        if state_url == "":
            continue
        log.info(f"State URL: {state_url}")
        response = request_with_retries(state_url)
        body = html.fromstring(response.text, "lxml")
        city_urls = city_urls + body.xpath('//tr/td/a[contains(@href, "/city/")]/@href')

    log.info(f"total cities = {len(city_urls)}")

    store_urls = []
    for city_url in city_urls:
        log.info(f"City URL: {city_url}")
        response = request_with_retries(city_url)
        body = html.fromstring(response.text, "lxml")
        for url in body.xpath('//a[contains(@class, "btn_red")]/@href'):
            if url not in store_urls and "/shelter/" in url:
                store_urls.append(url)

    return store_urls


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
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
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_text(body, xpath, replaceW=None):
    sel = body.xpath(xpath)
    if len(sel) == 0:
        return MISSING

    else:
        sel = sel[0]
        if replaceW is not None:
            sel = sel.replace(replaceW, "")
        sel = sel.strip()
        if len(sel) == 0:
            return MISSING
        return sel


def get_data(page_url, sgw: SgWriter):

    log.debug(f"Scrapping {page_url} ...")
    response = request_with_retries(page_url)
    body = html.fromstring(response.text, "lxml")

    store_number = MISSING
    location_type = "Shelter"
    latitude = MISSING
    longitude = MISSING
    country_code = "US"

    try:
        location_name = body.xpath('//h1[@class="entry_title"]/text()')[0]
    except:
        location_name = get_text(body, "//h1/text()")

    # Website has some Test pages which are not useful for data, skipped these
    if "TEST" not in str(location_name) and "Test Clinic" not in str(location_name):

        raw_address = body.xpath('//div[@class="col col_4_of_12"]/p/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        raw_address = ", ".join(raw_address)
        if raw_address == ",  -":
            raw_address = MISSING

        street_address, city, state, zip_postal = get_address(raw_address)
        phone = get_text(body, '//a[contains(@href, "tel:")]/@href', "tel:")
        if "ext" in phone.lower():
            phone = (phone.lower()).split("ext")[0]
        if "or" in phone.lower():
            phone = (phone.lower()).split("or")[0]
        if "()" in phone:
            phone = phone.replace("()", "")

        hours = body.xpath('//div[@class="col col_12_of_12 hours"]/ul/li')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("text()")).strip()
            time = "".join(hour.xpath("span/text()")).strip()
            time = re.sub(r"\s+", " ", time, flags=re.UNICODE)
            hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(hours_list).strip()

        # To handle PO BOX address where lib failed
        if "p.o" in raw_address.lower():
            street_address = raw_address.split(",")[0]

        if street_address is MISSING and "box" in raw_address.lower():
            street_address = raw_address.split(",")[0]

        row = SgRecord(
            locator_domain=DOMAIN,
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

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = fetch_stores()
    log.info(f"Total stores = {len(urls)}")

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
