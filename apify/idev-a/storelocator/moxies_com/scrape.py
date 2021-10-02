from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("moxies")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://moxies.com"
base_url = "https://moxies.com/location-finder?usredirect=no"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link["href"])
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
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div#content-area div.call-location-block__city ul li > a")
    logger.info(f"{len(links)} found")
    for page_url, soup1 in fetchConcurrentList(links):
        logger.info(page_url)
        ss = json.loads(soup1.find("script", type="application/ld+json").string)
        addr = ss["address"]
        location_type = ""
        src = soup1.select_one("div.intro-banner picture img")["srcset"]
        if "TempClosure" in src:
            location_type = "Temporarily Closed"
        yield SgRecord(
            page_url=page_url,
            location_name=ss["name"].replace("’", "'"),
            street_address=addr["streetAddress"],
            city=addr["addressLocality"].replace("’", "'"),
            state=addr["addressRegion"],
            latitude=ss["geo"]["latitude"],
            longitude=ss["geo"]["longitude"],
            zip_postal=addr["postalCode"],
            country_code=addr["addressCountry"],
            phone=ss["telephone"],
            locator_domain=locator_domain,
            location_type=location_type,
            hours_of_operation="; ".join(ss["openingHours"]).replace("–", "-"),
        )


if __name__ == "__main__":
    data = fetch_data()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)
