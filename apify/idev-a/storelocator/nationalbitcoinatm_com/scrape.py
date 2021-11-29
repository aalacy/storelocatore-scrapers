from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re

logger = SgLogSetup().get_logger("nationalbitcoinatm")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.nationalbitcoinatm.com/bitcoin-atm-near-me/"
locator_domain = "https://www.nationalbitcoinatm.com"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = link.a["href"]
    response = request_with_retries(page_url)
    return page_url, link, bs(response.text, "lxml")


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
    return session.get(url, headers=_headers)


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div.locations-map-list div.locations-map-item")
    logger.info(f"{len(links)} found")
    for page_url, link, sp1 in fetchConcurrentList(links):
        logger.info(page_url)
        raw_address = link.select_one(".locations-map-item__address").text.strip()
        addr = parse_address_intl(raw_address + ", USA")
        x = raw_address.rfind(addr.city)
        street_address = raw_address[:x].replace(",", "").strip()
        hours = ""
        _hr = sp1.find("p", string=re.compile(r"HOURS"))
        if _hr:
            hours = "; ".join(_hr.find_parent().find_next_sibling().stripped_strings)
        yield SgRecord(
            page_url=page_url,
            store_number=link.select_one("div.locations-map-item__number").text.strip(),
            location_name=link.select_one("h4").text.strip(),
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="US",
            locator_domain=locator_domain,
            latitude=link["data-lat"],
            longitude=link["data-lng"],
            hours_of_operation=hours.replace("–", "-"),
            raw_address=raw_address,
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
