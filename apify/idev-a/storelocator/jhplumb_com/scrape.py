from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jhplumbingdepot")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.jhplumbingdepot.com/contact/"
locator_domain = "https://www.jhplumbingdepot.com"
session = SgRequests().requests_retry_session()
max_workers = 12


def fetchConcurrentSingle(link):
    if link.get("value"):
        page_url = link.get("value")
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
    links = soup.select("select.mob-mb2 option")
    logger.info(f"{len(links)} found")
    for page_url, sp1 in fetchConcurrentList(links):
        logger.info(page_url)
        yield SgRecord(
            page_url=page_url,
            location_name=sp1.select_one('span[itemprop="name"]').text.strip(),
            street_address=sp1.select_one(
                'span[itemprop="streetAddress"]'
            ).text.strip(),
            city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
            zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
            country_code="UK",
            phone=sp1.select_one('span[itemprop="telephone"]').text.strip(),
            locator_domain=locator_domain,
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
