from sgscrape.sgpostal import parse_address_intl
from lxml import html
from concurrent.futures import ThreadPoolExecutor
import math
import time
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "progressive.com"
MISSING = "<MISSING>"
start_url = "https://www.progressive.com/agent/local-agent"
max_workers = 3

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests(proxy_rotation_failure_threshold=10)
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetchConcurrentSingle(url):
    data = {"url": url}
    response = request_with_retries(data["url"])
    body = html.fromstring(response.text, "lxml")
    return {"data": data, "body": body, "response": response.text}


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = 100
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            count = count + 1
            if count % reminder == 0:
                log.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def fetchStores():
    response = request_with_retries(start_url)
    body = html.fromstring(response.text, "lxml")
    stateUrls = body.xpath("//ul[@class='state-list']/li/a/@href")
    log.debug(f"total states= {len(stateUrls)}")

    cityUrls = []
    for city in fetchConcurrentList(stateUrls):
        cityUrls = cityUrls + city["body"].xpath("//ul[@class='city-list']/li/a/@href")
    log.debug(f"total cities= {len(cityUrls)}")

    page_urls = []
    for page in fetchConcurrentList(cityUrls):
        page_urls = page_urls + page["body"].xpath(
            "//a[@class='list-link details']/@href"
        )
    log.debug(f"total stores= {len(page_urls)}")

    return page_urls


def getAddress(raw_address):
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
        log.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetchData():
    page_urls = fetchStores()
    log.info(f"Total stores = {len(page_urls)}")

    for detail in fetchConcurrentList(page_urls):
        page_url = detail["data"]["url"]
        body = detail["body"]
        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        country_code = "US"

        location_name = "".join(body.xpath("//h1/text()")).strip()
        phone = "".join(
            body.xpath("//dt[text()='Phone:']/following-sibling::dd/a/text()")
        ).strip()

        raw_address = "".join(
            body.xpath("//dt[text()='Address:']/following-sibling::dd/text()")
        ).strip()

        street_address, city, state, zip_postal = getAddress(raw_address)

        hours = body.xpath(
            "//div[./h2[text()='Office Hours']]/following-sibling::div[1]//dl/div"
        )
        hoo = []
        for hour in hours:
            day = "".join(hour.xpath("./dt/text()")).strip()
            time = "".join(hour.xpath("./dd/text()")).strip()
            hoo.append(f"{day} {time}")

        hours_of_operation = ";".join(hoo) or MISSING

        yield SgRecord(
            locator_domain=website,
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
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    count = 0
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetchData():
            writer.write_row(rec)
            count = count + 1
    end = time.time()
    log.info(f"Scrape took {end-start} seconds. total store = {count}")


if __name__ == "__main__":
    scrape()
