import json
from typing import Iterable
from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton


website = "visionexpress_com"
logger = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.visionexpress.com"
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://www.visionexpress.com/store-overview"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.find("article").findAll("a")
    for state_url in state_list:
        logger.info(f"Fetching from: {state_url.text}")
        state_url = state_url["href"]
        if state_url.count("/") > 4:
            store_url_list.append(state_url)
            logger.info(state_url)
            state.push_request(SerializableRequest(url=state_url))
        else:
            r = http.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "location-item__actions"})
            for loc in loclist:
                loc = DOMAIN + loc.findAll("a")[-1]["href"]
                store_url_list.append(loc)
                logger.info(loc)
                state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        logger.info(f"Pulling the data from: {next_r.url}")
        page_url = next_r.url
        try:
            schema = r.text.split('<script type="application/ld+json">')[2].split(
                "</script>", 1
            )[0]
        except:
            r = http.get(next_r.url, headers=headers)
            schema = r.text.split('<script type="application/ld+json">')[2].split(
                "</script>", 1
            )[0]
        schema = schema.replace("\n", "")
        loc = json.loads(schema)
        location_name = loc["name"]
        address = loc["address"][0]
        phone = loc["telephone"]
        street_address = address["streetAddress"].replace("undefined", "")
        city = address["addressLocality"]
        state = MISSING
        zip_postal = address["postalCode"]
        country_code = address["addressCountry"]
        coords = r.text.split('"lat":')[1].split(',"emailAddress":')[0].split(',"lon":')
        latitude = coords[0]
        longitude = coords[1]
        try:
            hours_of_operation = (
                soup.findAll("dl", {"class": "location-opening-hours__list"})[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            hours_of_operation = (
                soup.find("dl", {"class": "location-opening-hours__list"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        store_number = MISSING
        location_type = MISSING
        raw_address = MISSING
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
