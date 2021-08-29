import re
import usaddress
from typing import Iterable
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton


DOMAIN = "petsmart.com"
logger = SgLogSetup().get_logger(logger_name="partycity_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

session = SgRequests()
MISSING = SgRecord.MISSING


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    url = "https://www.petsmart.com/stores/us/"
    store_url_list = []
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    state_list = soup.find("ul", {"class": "row states-list-content"}).findAll("a")
    for idx1, state_url in enumerate(state_list):
        logger.info(f"Fetching locations for {state_url.text}")
        state_url = state_url["href"]
        r2 = session.get(state_url, headers=headers, timeout=180)
        soup2 = BeautifulSoup(r2.text, "html.parser")
        loclist = soup2.findAll("a", {"class": "store-details-link"})
        for loc in loclist:
            loc = "https://www.petsmart.com/stores/us/" + loc["href"]
            store_url_list.append(loc)
            logger.info(loc)
            state.push_request(SerializableRequest(url=loc))
    return True


def fetch_records(session: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        r = session.get(next_r.url, headers=headers, allow_redirects=True, timeout=180)
        if r.url == "https://www.petsmart.com/store-locator/":
            continue
        logger.info(f"Pulling the data from: {r.url}")
        soup = BeautifulSoup(r.text, "html.parser")
        page_url = r.url
        location_name = soup.find("h1").text
        if "Closed" in location_name:
            continue
        raw_address = (
            soup.find("p", {"class": "store-page-details-address"})
            .findAll("span")[1]
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        address = raw_address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street_address = ""
        city = ""
        state = ""
        zip_postal = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street_address = street_address + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                zip_postal = zip_postal + " " + temp[0]
            i += 1
        country_code = "US"
        phone = soup.find("p", {"class": "store-page-details-phone"}).text
        try:
            hours_of_operation = (
                soup.find("div", {"class": "store-page-details-hours-container"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            hours_of_operation = MISSING
        latitude, longitude = re.findall(
            r"center=([\d\.]+),([\-\d\.]+)",
            soup.find("div", class_="store-page-map mapViewstoredetail")
            .find("img")
            .get("src"),
        )[0]
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
