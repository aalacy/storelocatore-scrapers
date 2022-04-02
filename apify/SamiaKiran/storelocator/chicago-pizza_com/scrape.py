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

session = SgRequests()
website = "chicago-pizza_com"
logger = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.chicago-pizza.com"
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    store_url_list = []
    url = "https://www.chicago-pizza.com/shop/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.findAll("ul", {"class": "citylist"})
    for state_url in state_list:
        city_list = state_url.findAll("li")
        for city_url in city_list:
            city_url = city_url.find("a")["href"]
            r = session.get(city_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                loclist = soup.find("ul", {"class": "shoplist"}).findAll("li")
            except:
                continue
            for loc in loclist:
                loc = loc.find("a")["href"]
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
        temp = soup.find("div", {"class": "detailbox"})
        phone = (
            temp.find("p", {"class": "phonenum"})
            .get_text(separator="|", strip=True)
            .replace("|", "")
        )
        location_name = (
            temp.find("h2").get_text(separator="|", strip=True).replace("|", "")
        )
        address = temp.find("address").get_text(separator="|", strip=True).split("|")
        raw_address = address[0]
        hours_of_operation = address[1].split("］")[1]
        # Parse the address
        pa = parse_address_intl(raw_address)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING
        store_number = MISSING
        location_type = MISSING
        country_code = "Japan"
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
            latitude=MISSING,
            longitude=MISSING,
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
