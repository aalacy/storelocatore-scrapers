from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("greenmill")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.greenmill.com/locations/"
locator_domain = "https://www.greenmill.com"
session = SgRequests().requests_retry_session()
max_workers = 2


def fetchConcurrentSingle(link):
    page_url = link["href"]
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
    links = soup.select("div.loc-container a")
    logger.info(f"{len(links)} found")
    for page_url, sp1 in fetchConcurrentList(links):
        logger.info(page_url)
        hours = []
        _hr = sp1.find("h4", string=re.compile(r"HOURS OF OPERATION"))
        if _hr:
            for hh in _hr.find_next_siblings("p"):
                if "menu" in hh.text or "Hours" in hh.text:
                    break
                temp = []
                for hr in hh.stripped_strings:
                    if "Kitchen" in hr:
                        continue
                    temp.append(hr)
                hours.append(" ".join(temp))
        if sp1.select_one('div[itemprop="name"]'):
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=sp1.select_one(
                    'div[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                country_code="US",
                phone=sp1.select_one('span[itemprop="telephone"]').text.strip(),
                locator_domain=locator_domain,
                latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
                longitude=sp1.select('meta[itemprop="latitude"]')[1]["content"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )
        else:
            addr = list(
                sp1.find("h3", string=re.compile(r"ADDRESS"))
                .find_next_sibling("p")
                .stripped_strings
            )
            coord = (
                sp1.select_one("div.mapbox iframe")["data-lazy-src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!2m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.h1.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[3],
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
