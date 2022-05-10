from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://schnitz.com.au/locations/"
locator_domain = "https://schnitz.com.au"

max_workers = 16


def fetchConcurrentSingle(link):
    if link.a:
        page_url = link.select_one("a.store-card__link")["href"]
        logger.info(page_url)
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
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.store-card")
        logger.info(f"{len(links)} found")
        for page_url, link, sp1 in fetchConcurrentList(links):
            if (
                sp1.select_one("span.crumb-collective__header-link")
                and "soon!" in sp1.select_one("span.crumb-collective__header-link").text
            ):
                continue
            raw_address = (
                link.select_one("div.store-card__address")
                .text.replace("\n", " ")
                .replace("\r", " ")
                .strip()
            )
            if "Australia" not in raw_address:
                raw_address += ", Australia"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            coord = sp1.select_one("div.single-store-content__map-map")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("ul.single-store-content__details-oh-list li")
                if "Anzac" not in hh.text
            ]

            phone = ""
            if link.select_one("a.store-card__phone"):
                phone = link.select_one("a.store-card__phone").text.strip()
            yield SgRecord(
                page_url=page_url,
                location_name=link.h4.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="AUS",
                phone=phone,
                locator_domain=locator_domain,
                latitude=coord["data-lat"],
                longitude=coord["data-lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
