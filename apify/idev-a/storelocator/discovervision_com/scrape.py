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

logger = SgLogSetup().get_logger("discovervision")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.discovervision.com/our-locations/"
locator_domain = "https://www.discovervision.com/"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = link.a["href"]
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
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div.loc_area div.loc_wrap")
    logger.info(f"{len(links)} found")
    for page_url, link, sp1 in fetchConcurrentList(links):
        logger.info(page_url)
        _hr = sp1.find("strong", string=re.compile(r"HOURS", re.IGNORECASE))
        if not _hr:
            _hr = sp1.find("strong", string=re.compile(r"Hours", re.IGNORECASE))
        if not _hr:
            _hr = sp1.find_all("", string=re.compile(r"HOURS"))[-1]
        hours = []
        if _hr:
            try:
                hours = list(_hr.find_parent("p").stripped_strings)[1:]
            except:
                import pdb

                pdb.set_trace()

        try:
            coord = (
                sp1.select_one("div#content_area iframe")["src"]
                .split("!2d")[1]
                .split("!2m")[0]
                .split("!3d")
            )
        except:
            coord = ["", ""]
        yield SgRecord(
            page_url=page_url,
            location_name=link.h3.text.strip(),
            street_address=" ".join(
                link.select_one('span[itemprop="streetAddress"]').stripped_strings
            ),
            city=link.select_one('span[itemprop="addressLocality"]')
            .text.replace(",", "")
            .strip(),
            state=link.select_one('span[itemprop="addressRegion"]')
            .text.replace(",", "")
            .strip(),
            zip_postal=link.select_one('span[itemprop="postalCode"]')
            .text.replace(",", "")
            .strip(),
            country_code="US",
            phone=link.select_one('span[itemprop="telephone"]').text.strip(),
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
