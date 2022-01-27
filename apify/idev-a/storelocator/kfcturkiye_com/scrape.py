from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfcturkiye")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://kfcturkiye.com/restoranlar"
locator_domain = "https://kfcturkiye.com"
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link.a["href"])
    response = request_with_retries(page_url)
    return page_url, bs(response.text, "lxml")


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
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
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.restaurants-item")
        logger.info(f"{len(links)} found")
        for page_url, sp1 in fetchConcurrentList(links):
            logger.info(page_url)
            raw_address = sp1.select_one("div.restaurant-detail-area p").text.strip()
            addr = parse_address_intl(raw_address + ", Turkey")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = [
                hh.text.strip()
                for hh in sp1.select("div.working-hours-info div.hours-item")
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one(
                    "div.restaurant-detail-area h3"
                ).text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Turkey",
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
