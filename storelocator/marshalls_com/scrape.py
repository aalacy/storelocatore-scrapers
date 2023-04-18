from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("marshalls")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.marshalls.com"
base_url = "https://www.marshalls.com/us/store/stores/allStores.jsp"

max_workers = 8
session = SgRequests().requests_retry_session()


def fetchConcurrentSingle(data):
    page_url = locator_domain + data["href"].replace("/m/", "/store/")
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
    links = soup.select("li.storelist-item a")
    logger.info(f"{len(links)} found")
    for page_url, sp1 in fetchConcurrentList(links):
        if sp1.select_one("div.store-comment"):
            continue
        logger.info(page_url)
        yield SgRecord(
            page_url=page_url,
            location_name=sp1.select_one("div.directions-header-store-name h1")
            .text.replace("Marshalls", "")
            .strip(),
            street_address=sp1.select_one(".street-address").text.strip(),
            city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
            state=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
            zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
            country_code="US",
            phone=sp1.select_one("div.tel").text.strip(),
            locator_domain=locator_domain,
            latitude=sp1.select_one("input#lat")["value"],
            longitude=sp1.select_one("input#long")["value"],
            hours_of_operation=sp1.select_one("div.store-hours").text,
        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
