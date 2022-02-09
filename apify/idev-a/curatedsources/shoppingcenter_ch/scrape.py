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

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://shoppingcenter.ch/"
locator_domain = "https://shoppingcenter.ch"

max_workers = 16


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link.a["href"])
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
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select(
            "div.view-id-shoppingcenters.view-display-id-attachment_1 > div > div"
        )
        logger.info(f"{len(links)} found")
        for page_url, link, sp1 in fetchConcurrentList(links):
            logger.info(page_url)
            raw_address = " ".join(sp1.select_one("div.adr").stripped_strings)
            phone = ""
            if sp1.select_one("div.tel a"):
                phone = sp1.select_one("div.tel a").text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=link.select_one("div.views-field-title a").text.strip(),
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                country_code="Switzerland",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
