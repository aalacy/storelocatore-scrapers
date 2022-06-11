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
import re

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://prch.org.pl/pl/katalog-ch"
locator_domain = "https://prch.org.pl/pl/katalog-ch"
max_workers = 32


def fetchConcurrentSingle(link):
    page_url = urljoin("https://prch.org.pl", link.a["href"])
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


def _g(sp1, txt):
    val = ""
    try:
        val = (
            sp1.find("td", string=re.compile(re.compile(re.escape(txt))))
            .find_next_sibling()
            .text.strip()
        )
    except:
        pass
    if val == "-":
        val = ""
    return val


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("li.mall-item")
        logger.info(f"{len(links)} found")
        for page_url, link, sp1 in fetchConcurrentList(links):
            logger.info(page_url)
            location_type = ""
            if _g(sp1, "Status") != "Otwarte":
                location_type = _g(sp1, "Status")

            if location_type == "W budowie":
                continue

            yield SgRecord(
                page_url=page_url,
                location_name=link.text.strip(),
                street_address=_g(sp1, "Adres"),
                city=_g(sp1, "Miasto"),
                state=_g(sp1, "Adres"),
                zip_postal=_g(sp1, "Kod pocztowy"),
                country_code="Poland",
                phone=_g(sp1, "Telefon"),
                locator_domain=locator_domain,
                location_type=location_type,
                latitude=link["data-lat"],
                longitude=link["data-lng"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
