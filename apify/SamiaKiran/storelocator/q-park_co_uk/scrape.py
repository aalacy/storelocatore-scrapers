import json
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton

DOMAIN = "https://www.q-park.co.uk"
logger = SgLogSetup().get_logger(logger_name="q-park_co_uk")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url_list = []
    url = "https://www.q-park.co.uk/en-gb/cities/"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("div", {"class": "col-xs-12 col-md-4 city"})
    for idx1, state_url in enumerate(state_list):
        state_url = state_url.find("a")["href"]
        state_url = DOMAIN + state_url
        r = http.get(state_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("li", {"class": "card"})
        for loc in loclist:
            try:
                loc = DOMAIN + loc.find("a")["href"]
            except:
                continue
            if "poi" in loc:
                continue
            if loc in url_list:
                continue
            url_list.append(loc)
            store_url_list.append(loc)
            logger.info(loc)
            state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        logger.info(f"Pulling the data from: {next_r.url}")
        page_url = next_r.url
        soup = BeautifulSoup(r.text, "html.parser")
        temp = (
            soup.findAll("script", {"type": "application/ld+json"})[1]
            .text.strip()
            .replace("\n", "")
        )
        temp = json.loads(temp)
        hours_of_operations = temp["openingHours"]
        hours_of_operations = " ".join(hours_of_operations)
        if hours_of_operations == "Mo-Su":
            hours_of_operations = "Mo-Su 24-7"
        address = temp["address"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        zip_postal = address["postalCode"]
        state = MISSING
        country_code = address["addressCountry"]
        location_name = temp["name"]
        store_number = MISSING
        location_type = MISSING
        raw_address = MISSING
        phone = MISSING
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
            phone=phone,
            location_type=location_type,
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=hours_of_operations,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    state = CrawlStateSingleton.get_instance()
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
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
