from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("eurocarparts")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.eurocarparts.com/store-locator"
locator_domain = "https://www.eurocarparts.com"
session = SgRequests().requests_retry_session()
max_workers = 12


def fetchConcurrentSingle(link):
    page_url = link["href"]
    if page_url.startswith("http"):
        response = request_with_retries(page_url)
        return page_url, response.text, bs(response.text, "lxml")


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
    links = soup.select("div.alpha-finder div.alpha-row a")
    logger.info(f"{len(links)} found")
    for page_url, res, sp1 in fetchConcurrentList(links):
        logger.info(page_url)
        addr = list(sp1.select_one("div.address-details p").stripped_strings)
        hours = []
        for hh in sp1.select("div.timing-table")[0].select("div.row"):
            hours.append(
                f"{hh.span.text.strip()}: {''.join(hh.select_one('span.col-two').stripped_strings)}"
            )
        coord = res.split("maps.LatLng(")[1].split(")")[0].split(",")
        state = ""
        if len(addr) > 4:
            state = addr[3].replace(",", " ")
        yield SgRecord(
            page_url=page_url,
            location_name=addr[0],
            street_address=addr[1]
            .replace(",", " ")
            .replace("\n", "")
            .replace("\t", ""),
            city=addr[2].replace(",", " "),
            state=state,
            zip_postal=addr[-1],
            country_code="CA",
            phone=sp1.select_one('span[itemprop="telephone"]').text.strip(),
            locator_domain=locator_domain,
            latitude=coord[0],
            longitude=coord[1],
            hours_of_operation="; ".join(hours).replace("–", "-"),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
