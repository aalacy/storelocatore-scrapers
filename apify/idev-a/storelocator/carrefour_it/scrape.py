from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefour.it"
base_url = "https://www.carrefour.it/on/demandware.store/Sites-carrefour-IT-Site/it_IT/StoreLocator-GetAll"


max_workers = 32


def fetchConcurrentSingle(link):
    page_url = locator_domain + link["Url"]
    logger.info(page_url)
    response = request_with_retries(page_url)
    if response.status_code == 200:
        return page_url, link, bs(response.text, "lxml")
    return None


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


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for page_url, _, sp1 in fetchConcurrentList(locations):
            hours = []
            for day, hh in _["Orari"].items():
                hours.append(f"{day}: {hh}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["Id"],
                location_name=_["Insegna"],
                street_address=_["Descrizione"].split("-")[0],
                city=_["Citta"],
                zip_postal=_["CAP"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code="IT",
                phone=_p(
                    sp1.select_one(
                        "div.content-store-info div.content-item span.item-text"
                    ).text.strip()
                ),
                location_type=_["Type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
