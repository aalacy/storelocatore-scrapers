from typing import Iterable
from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton


website = "pharmacy_kmart_com"
logger = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://pharmacy.kmart.com/"
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://www.kmart.com/stores.html"
    store_url_list = []
    http = SgRequests()
    r = http.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("li", {"class": "sbs-state"})
    for state_url in state_list:
        temp_state = state_url.find("span").text
        logger.info(f"Fetching from: {temp_state}")
        state_url = "https://www.kmart.com" + state_url.find("a")["href"]
        r = http.get(state_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "li", {"class": "shc-quick-links--store-details__list--stores"}
        )
        for loc in loclist:
            loc = "https://www.kmart.com" + loc.find("a")["href"]
            store_url_list.append(loc)
            logger.info(loc)
            state.push_request(SerializableRequest(url=loc, json=temp_state))
    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        state = next_r.json
        r = http.get(next_r.url, headers=headers)
        page_url = next_r.url
        logger.info(f"Pulling the data from: {next_r.url}")
        soup = BeautifulSoup(r.text, "html.parser")
        location_name = soup.find("h1", {"class": "shc-save-store__title"})
        store_number = location_name["data-unit-number"]
        location_name = (
            location_name["data-store-title"]
            + " "
            + location_name["data-city"]
            + " "
            + location_name["data-unit-number"]
        )
        raw_address = (
            soup.find("p", {"class": "shc-store-location__details--address"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        pa = parse_address_intl(raw_address)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING
        country_code = "US"
        latitude, longitude = (
            soup.find("a", {"class": "shc-store-location__details--direction"})["href"]
            .split("&daddr=")[1]
            .split(",")
        )
        phone = soup.find("strong", {"class": "shc-store-location__details--tel"}).text
        hours_of_operation = (
            soup.find("div", {"class": "shc-store-hours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Store Hours ", "")
        )
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
            location_type=MISSING,
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
