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


base_url = "https://www.lojj.pt/shoppings/{}/"
locator_domain = "https://lojj.pt/shoppings"
max_workers = 16


def fetchConcurrentSingle(link):
    page_url = urljoin("https://lojj.pt", link.a["href"])
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
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("div.listBox")
            if not links:
                break
            page += 1
            logger.info(f"{len(links)} found")
            for page_url, link, sp1 in fetchConcurrentList(links):
                logger.info(page_url)
                addr = list(link.p.stripped_strings)
                phone = ""
                if link.select_one('span[itemprop="telephone"]'):
                    phone = link.select_one('span[itemprop="telephone"]').text.strip()

                hours_of_operation = ""
                if sp1.select_one('meta[itemprop="openingHours"]'):
                    hours_of_operation = sp1.select_one(
                        'meta[itemprop="openingHours"]'
                    )["content"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.h2.text.strip(),
                    street_address=addr[0],
                    city=addr[1].split()[-1].strip(),
                    zip_postal=addr[1].split()[0].strip(),
                    country_code="Portugal",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
                    longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
                    hours_of_operation=hours_of_operation,
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
