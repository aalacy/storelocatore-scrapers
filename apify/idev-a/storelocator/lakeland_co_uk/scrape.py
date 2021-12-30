from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("lakeland")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.lakeland.co.uk/assets/scripts/store-locator.js"
locator_domain = "https://www.lakeland.co.uk"
session = SgRequests().requests_retry_session()
max_workers = 12


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link[-1])
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
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    links = json.loads(
        session.get(base_url, headers=_headers)
        .text.split("ArrLocations:")[1]
        .split("ObjGeocoder:")[0]
        .strip()[:-1]
    )
    logger.info(f"{len(links)} found")
    for page_url, _, sp1 in fetchConcurrentList(links):
        logger.info(page_url)
        hours = []
        for hh in sp1.select("div.store-times-disabled table tr"):
            if not hh.select("td")[1].text.strip():
                continue
            hours.append(hh["datetime"])

        city = zip_postal = street_address = ""
        if sp1.select_one('span[itemprop="addressRegion"]'):
            city = sp1.select_one('span[itemprop="addressRegion"]').text.strip()
        elif sp1.select_one('span[itemprop="addressLocality"]'):
            city = sp1.select_one('span[itemprop="addressLocality"]').text.strip()
        if sp1.select_one('span[itemprop="postalCode"]'):
            zip_postal = sp1.select_one('span[itemprop="postalCode"]').text.strip()
        if sp1.select_one('span[itemprop="streetAddress"]'):
            street_address = (
                sp1.select_one('span[itemprop="streetAddress"]')
                .text.replace("’", "'")
                .replace("\n", "")
                .replace(",", " ")
                .strip()
            )
        location_type = ""
        if (
            sp1.select_one('div[itemprop="description"]')
            and "is now closed" in sp1.select_one('div[itemprop="description"]').text
        ):
            location_type = "closed"
            hours = []
        yield SgRecord(
            page_url=page_url,
            location_name=_[0],
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            country_code="uk",
            phone=sp1.select_one('p[itemprop="telephone"]').text.strip(),
            locator_domain=locator_domain,
            latitude=_[1],
            longitude=_[2],
            location_type=location_type,
            hours_of_operation="; ".join(hours).replace("–", "-"),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
