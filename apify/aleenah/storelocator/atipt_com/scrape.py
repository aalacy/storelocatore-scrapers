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


website = "atipt_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.atipt.com/"
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    store_url_list = []
    http = SgRequests()
    res = http.get("https://locations.atipt.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    states = soup.find("ul", {"class": "list-unstyled"}).find_all("a")
    for state_url in states:
        log.info(f"Fetching Stores from State {state_url.text}....")
        res = http.get("https://locations.atipt.com" + state_url.get("href"))
        soup = BeautifulSoup(res.text, "html.parser")
        cities = soup.find("ul", {"class": "list-unstyled"}).find_all("a")
        for city_url in cities:
            res = http.get("https://locations.atipt.com" + city_url.get("href"))
            soup = BeautifulSoup(res.text, "html.parser")
            stores = soup.find_all("a", {"class": "name"})
            for store in stores:
                loc = "https://locations.atipt.com" + store.get("href")
                store_url_list.append(loc)
                log.info(loc)
                state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = http.get(next_r.url, headers=headers)
        log.info(f"Pulling the data from: {next_r.url}")
        page_url = next_r.url
        soup = BeautifulSoup(r.text, "html.parser")
        jso = soup.find("script", {"type": "application/ld+json"}).text.split('"name"')[
            1
        ]
        jso = '{"name"' + jso
        jso = json.loads(jso)
        addr = jso["address"]
        city = addr["addressLocality"]
        state = addr["addressRegion"]
        zip_postal = addr["postalCode"]
        street_address = addr["streetAddress"]
        latitude = jso["geo"]["latitude"]
        longitude = jso["geo"]["longitude"]
        location_type = jso["name"]
        phone = jso["telephone"]
        location_name = jso["name"]
        hours_of_operation = (
            str(jso["openingHours"])
            .replace("','", " ")
            .replace("['", " ")
            .replace("']", " ")
        )
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
    log.info("Started")
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

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
