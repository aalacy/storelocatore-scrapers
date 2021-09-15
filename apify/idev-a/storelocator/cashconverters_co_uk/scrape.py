from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("cashconverters")

locator_domain = "https://www.cashconverters.co.uk"
base_url = "https://www.cashconverters.co.uk/c3api/store/query"

_headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
}
session = SgRequests(proxy_country="gb").requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = locator_domain + link["link"]
    response = request_with_retries(page_url)
    return page_url, link, response


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
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    locations = session.get(base_url, headers=_headers).json()["Value"]
    logger.info(f"{len(locations)} found")
    for page_url, _, res in fetchConcurrentList(locations):
        if "stores/" not in res.url or res.status_code != 200:
            continue
        logger.info(page_url)
        addr = _["addressline2"].split()
        sp1 = bs(res.text, "lxml")
        hours = []
        if sp1.select("div.store-detail__hours--body"):
            for hh in list(
                sp1.select("div.store-detail__hours--body")[0].stripped_strings
            ):
                if "holiday" in hh.lower() or "bank" in hh.lower():
                    break
                hours.append(hh)
        yield SgRecord(
            page_url=res.url,
            location_name=_["title"],
            street_address=_["addressline1"],
            city=addr[0],
            state=" ".join(addr[1:-2]),
            zip_postal=" ".join(addr[-2:]),
            country_code="UK",
            phone=_["phone"],
            latitude=_["lat"],
            longitude=_["lng"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours).replace("–", "-"),
            raw_address=_["addressline1"] + " " + _["addressline2"],
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
