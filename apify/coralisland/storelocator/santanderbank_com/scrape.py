import json
from lxml import html
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton

DOMAIN = "https://santanderbank.com/"
logger = SgLogSetup().get_logger(logger_name="santanderbank_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://locations.santanderbank.com/"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.find("div", {"class": "browse-wrap"}).findAll("a")
    for idx1, state_url in enumerate(state_list[0:]):
        logger.info(f"Fetching from : {state_url.text}")
        state_url = state_url["href"]
        r = http.get(state_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        city_list = soup.find("div", {"class": "locator block-padding"}).findAll("a")
        for city_url in city_list:
            city_url = city_url["href"]
            r = http.get(city_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.find("ul", {"class": "city-map-list"}).findAll(
                "a", {"class": "more-info"}
            )
            for loc in loclist:
                loc = loc["href"]
                store_url_list.append(loc)
                logger.info(loc)
                state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        location_name = soup.find("h2", {"class": "location-name"}).text
        logger.info(f"Pulling the data from: {next_r.url}")
        sel = html.fromstring(r.text, "lxml")
        js = sel.xpath("//script[@type='application/ld+json']/text()")
        js = "".join(js)
        loc = json.loads(js)[0]
        page_url = next_r.url
        country_code = "US"
        address = loc["address"] or MISSING
        street_address = address["streetAddress"] or MISSING
        city = address["addressLocality"] or MISSING
        state = address["addressRegion"] or MISSING
        zip_postal = address["postalCode"] or MISSING
        phone = address["telephone"] or MISSING
        coords = loc["geo"]
        latitude = coords["latitude"] or MISSING
        longitude = coords["longitude"] or MISSING
        hours_of_operation = loc["openingHours"] or MISSING
        store_number = MISSING
        location_type = soup.find("div", {"class": "location-type"}).find("span").text
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
        )
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
