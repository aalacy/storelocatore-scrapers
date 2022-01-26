from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tapi")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.tapi.co.uk/stores/search"
locator_domain = "https://www.tapi.co.uk"
session = SgRequests().requests_retry_session()
max_workers = 1


def fetchConcurrentSingle(link):
    page_url = urljoin("https://www.tapi.co.uk/", link["href"])
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
    return session.get(url, headers=_headers)


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div.stores-list.stores-list-all a")
    logger.info(f"{len(links)} found")
    for page_url, soup1 in fetchConcurrentList(links):
        logger.info(page_url)
        scripts = soup1.find_all("script", type="application/ld+json")
        ss = json.loads(scripts[0].contents[0])
        json_data = json.loads(scripts[1].contents[0])
        yield SgRecord(
            page_url=page_url,
            store_number=ss["branchCode"],
            location_name=ss["name"],
            street_address=ss["address"]["streetAddress"],
            city=ss["address"]["addressRegion"],
            zip_postal=ss["address"]["postalCode"],
            latitude=json_data["geo"]["latitude"],
            longitude=json_data["geo"]["longitude"],
            country_code=ss["address"]["addressCountry"],
            phone=ss["telephone"],
            location_type=ss["@type"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(ss["openingHours"]),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
