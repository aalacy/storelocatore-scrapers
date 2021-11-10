import re
import json
from typing import Iterable
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton


DOMAIN = "https://www.petco.com/unleashed"
logger = SgLogSetup().get_logger(logger_name="partycity_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

session = SgRequests()
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://stores.petco.com/"
    store_url_list = []
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("div", {"class": "map-list-item-wrap is-single"})
    for idx1, state_url in enumerate(state_list):
        logger.info(f"Fetching locations for {state_url.find('a').text}")
        state_url = state_url.find("a")["href"]
        r2 = session.get(state_url, headers=headers)
        soup2 = BeautifulSoup(r2.text, "html.parser")
        city_list = soup2.findAll("div", {"class": "map-list-item is-single"})
        for city_url in city_list:
            logger.info(f"Fetching locations for {city_url.find('a').text}")
            city_url = city_url.find("a")["href"]
            r3 = session.get(city_url, headers=headers)
            soup3 = BeautifulSoup(r3.text, "html.parser")
            loclist = soup3.findAll("a", string=re.compile("view details"))
            if len(loclist) == 1:
                loc = loclist[0]["href"]
                store_url_list.append(loc)
                logger.info(loc)
                state.push_request(SerializableRequest(url=loc))
            else:
                for loc in loclist:
                    loc = loc["href"]
                    store_url_list.append(loc)
                    logger.info(loc)
                    state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(session: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = session.get(next_r.url, headers=headers)
        location_type = MISSING
        if "(Temporarily Closed)" in r.text:
            location_type = "Temporarily Closed"
        logger.info(f"Pulling the data from: {next_r.url}")
        temp = r.text.split('<script type="application/ld+json" id="indy-schema">')[
            1
        ].split("</script>")[0]
        temp = json.loads(temp)
        temp = temp[0]
        location_name = temp["alternateName"][0]
        latitude = temp["geo"]["latitude"]
        longitude = temp["geo"]["longitude"]
        hours_of_operation = temp["openingHours"]
        address = temp["address"]
        street_address = address["streetAddress"]
        city = address["addressLocality"]
        state = address["addressRegion"]
        zip_postal = address["postalCode"]
        phone = address["telephone"]
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=next_r.url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=MISSING,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        with SgRequests() as session:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(session, state)
            )
            for rec in fetch_records(session, state):
                writer.write_row(rec)
                count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
