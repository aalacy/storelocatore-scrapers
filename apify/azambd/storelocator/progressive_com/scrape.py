from lxml import html
import time
from typing import Iterable

from sgpostal.sgpostal import parse_address_usa
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton

website = "progressive.com"
MISSING = "<MISSING>"
start_url = "https://www.progressive.com/agent/local-agent"


log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}


def fetch_stores(http: SgRequests, state: CrawlState) -> bool:
    response = http.get(start_url)
    body = html.fromstring(response.text, "lxml")
    stateUrls = body.xpath("//ul[@class='state-list']/li/a/@href")
    log.info(f"total states = {len(stateUrls)}")

    cityUrls = []  # type: ignore
    for stateUrl in stateUrls:
        response = http.get(stateUrl)
        body = html.fromstring(response.text, "lxml")
        cityUrls = cityUrls + body.xpath("//ul[@class='city-list']/li/a/@href")
    log.info(f"total cities = {len(cityUrls)}")

    count = 0
    for cityUrl in cityUrls:
        response = http.get(cityUrl)
        body = html.fromstring(response.text, "lxml")
        for page_url in body.xpath("//a[@class='list-link details']/@href"):
            state.push_request(SerializableRequest(url=page_url))
            count = count + 1
    log.info(f"total stores = {count}")

    return True


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
        log.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    http = SgRequests()
    for next_r in state.request_stack_iter():
        page_url = next_r.url
        log.info(f"Now Crawling: {page_url}")
        response = http.get(page_url, headers=headers)
        body = html.fromstring(response.text, "lxml")

        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        country_code = "US"

        location_name = "".join(body.xpath("//h1/text()")).strip()
        log.info(f"Location name: {location_name}")
        phone = "".join(
            body.xpath("//dt[text()='Phone:']/following-sibling::dd/a/text()")
        ).strip()

        raw_address = "".join(
            body.xpath("//dt[text()='Address:']/following-sibling::dd/text()")
        ).strip()

        street_address, city, state, zip_postal = get_address(raw_address)

        hours = body.xpath(
            "//div[./h2[text()='Office Hours']]/following-sibling::div[1]//dl/div"
        )
        hoo = []  # type: ignore
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


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    state = CrawlStateSingleton.get_instance()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: fetch_stores(http, state)
            )
            for rec in fetch_data(http, state):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds")


if __name__ == "__main__":
    scrape()
