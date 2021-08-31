from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import re
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("advanceamerica")
session = SgRequests().requests_retry_session()

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.advanceamerica.net"
base_url = "https://www.advanceamerica.net/sitemap"

max_workers = 8


def fetchConcurrentSingle(_):
    page_url = locator_domain + _.a["href"]
    return page_url, _, bs(request_with_retries(page_url).text, "lxml")


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
    with SgRequests() as session:
        states = (
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select("div.container > ul > li")[-1]
            .select("ul a")
        )
        for state in states:
            state_url = locator_domain + state["href"]
            locations = bs(
                session.get(state_url, headers=_headers).text, "lxml"
            ).select("div.alpha-list div.single-location div.location-details")
            for page_url, _, sp1 in fetchConcurrentList(locations):
                logger.info(f"[{state.text}] {page_url}")
                ss = json.loads(
                    sp1.find("script", string=re.compile(r"openingHours")).string
                )
                yield SgRecord(
                    page_url=page_url,
                    store_number=_.a.text.strip().split("#")[-1],
                    location_name=_.a.text.strip(),
                    street_address=ss["address"]["streetAddress"],
                    city=ss["address"]["addressLocality"],
                    state=ss["address"]["addressRegion"],
                    zip_postal=ss["address"]["postalCode"],
                    latitude=ss["geo"]["latitude"],
                    longitude=ss["geo"]["longitude"],
                    country_code="US",
                    phone=ss["telephone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(ss["openingHours"]),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
