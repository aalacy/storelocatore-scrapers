from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
import dirtyjson as json
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.castorama.fr"
base_url = "https://www.castorama.fr/magasin"

max_workers = 8


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link["href"])
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
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select('li[data-test-id="link-list-container"] a')
        logger.info(f"{len(links)} found")
        for page_url, sp1 in fetchConcurrentList(links):
            logger.info(page_url)
            _ = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = _["address"]
            hours = []
            for hh in _["openingHoursSpecification"]:
                if hh.get("opens"):
                    open = ":".join(hh["opens"].split(":")[:-1])
                    close = ":".join(hh["closes"].split(":")[:-1])
                    times = f"{open} - {close}"
                else:
                    times = "closed"
                hours.append(f"{hh['dayOfWeek']}: {times}")

            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("/")[-1],
                location_name=_["name"],
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                state=addr["addressRegion"],
                zip_postal=addr["postalCode"],
                country_code="FR",
                phone=_["telephone"],
                locator_domain=locator_domain,
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
