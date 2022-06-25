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
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = (
    "https://top-rated.online/countries/Lithuania/cities/Lithuania/Shopping+Centers"
)
base_url = (
    "https://top-rated.online/countries/Lithuania/cities/Lithuania/Shopping+Centers/{}"
)

max_workers = 12


def fetchConcurrentSingle(page_url):
    logger.info(page_url)
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
        links = []
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            if (
                soup.select_one("div.alert")
                and "Sorry" in soup.select_one("div.alert").text
            ):
                break
            page += 1
            links += [
                "https://top-rated.online" + ll["href"]
                for ll in soup.select("ol.list li a")
                if ll.get("href") and "/cities" in ll["href"]
            ]
        logger.info(f"{len(links)} found")
        for page_url, sp1 in fetchConcurrentList(links):
            raw_address = (
                sp1.find("h2", string=re.compile(r"^Address"))
                .find_next_sibling()
                .text.strip()
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            hr = sp1.find("h2", string=re.compile(r"^Working Hours"))
            if hr:
                for hh in hr.find_next_sibling().select("li"):
                    hours.append(hh.text.strip())

            location_type = "shopping center"
            if "store" in sp1.select_one("h1 a").text:
                location_type = "store"

            zip_postal = addr.postcode
            if "lv-1019" in raw_address.lower():
                zip_postal = "1019"
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one("h1 a").text.split("-")[0].strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_postal,
                country_code=addr.country or "Lithuania",
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
