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

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://shoppingtotal.ch/en/shopping-centers/page/{}/"
locator_domain = "https://shoppingtotal.ch/en/shopping-centers"

max_workers = 8


def fetchConcurrentSingle(link):
    page_url = link.a["href"]
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
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("div.page-content-main div.grid-item")
            logger.info(f"{len(links)} found")
            if not links:
                break
            page += 1
            for page_url, sp1 in fetchConcurrentList(links):
                logger.info(page_url)
                addr = []
                street_address = sp1.select_one("div.mall-strasse_nr").text.strip()
                city_zip = sp1.select_one("div.mall-plz_ort").text.strip()
                addr.append(street_address)
                addr.append(city_zip)

                phone = ""
                if sp1.select_one("div.mall-telefon"):
                    phone = sp1.select_one("div.mall-telefon").text.strip()
                country_code = "Liechtenstein"
                if sp1.find("", string=re.compile(r"Switzerland")):
                    country_code = "Switzerland"
                coord = sp1.select_one("div.mall-standort div.osm")
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=street_address,
                    city=" ".join(city_zip.split()[1:]),
                    zip_postal=city_zip.split()[0].strip(),
                    country_code=country_code,
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=coord["data-lat"],
                    longitude=coord["data-lng"],
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
