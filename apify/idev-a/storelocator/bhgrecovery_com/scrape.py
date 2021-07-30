from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import re
import math
from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("bhgrecovery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = f"https://www.bhgrecovery.com/locations/{link['hs_path']}"
    response = request_with_retries(page_url)
    return page_url, response.text


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
    locator_domain = "https://bhgrecovery.com/"
    base_url = "https://www.bhgrecovery.com/locations?lat=36.9138353&lon=-76.2826675&searched=23505"
    with SgRequests() as session:
        links = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var search_rows =")[1]
            .split("var sort_search_rows")[0]
            .strip()
        )
        logger.info(f"{len(links)} found")
        for page_url, res in fetchConcurrentList(links):
            logger.info(page_url)
            sp1 = bs(res, "lxml")
            ss = json.loads(
                sp1.find("script", type="application/ld+json").string.strip()
            )
            _hr = sp1.find("h5", string=re.compile(r"Hours of Operation"))
            hours = []
            if _hr:
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in _hr.find_next_sibling().select("p")
                ]
            yield SgRecord(
                page_url=page_url,
                location_name=ss["name"].replace("&#8211;", "-").replace("–", "-"),
                street_address=ss["address"]["streetAddress"],
                city=ss["address"]["addressLocality"],
                state=ss["address"]["addressRegion"],
                zip_postal=ss["address"]["postalCode"],
                country_code="US",
                phone=ss["telephone"],
                locator_domain=locator_domain,
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
