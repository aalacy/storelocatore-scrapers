from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("moes")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://locations.moes.com/?_ga=2.153993339.2122445182.1627930599-497689333.1627930599"
locator_domain = "https://www.moes.com/"
session = SgRequests().requests_retry_session()
max_workers = 12


def fetchConcurrentSingle(link):
    page_url = link["href"]
    if not page_url.startswith("http"):
        page_url = urljoin("https://locations.moes.com/", link["href"])
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


def _d(sp1, page_url):
    street_address = sp1.select_one("span.c-address-street-1").text.strip()
    if sp1.select_one("span.c-address-street-2"):
        street_address += " " + sp1.select_one("span.c-address-street-2").text.strip()
    hours = [hh["content"] for hh in sp1.select("table.c-hours-details tbody tr")]
    phone = ""
    if sp1.select_one("div#phone-main"):
        phone = sp1.select_one("div#phone-main").text.strip()
    state = ""
    if sp1.select_one(".c-address-state"):
        state = sp1.select_one(".c-address-state").text.strip()
    zip_postal = ""
    if sp1.select_one(".c-address-postal-code"):
        zip_postal = sp1.select_one(".c-address-postal-code").text.strip()
    return SgRecord(
        page_url=page_url,
        location_name=sp1.select_one("h1#location-name a").text.strip(),
        street_address=street_address.split(",")[0].strip(),
        city=sp1.select_one(".c-address-city").text.strip(),
        state=state,
        zip_postal=zip_postal,
        country_code=sp1.select_one(".c-address-country-name").text.strip(),
        phone=phone,
        latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
        longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours).replace("–", "-"),
    )


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    states = soup.select("ul.Directory-listLinks a")
    logger.info(f"{len(states)} found")
    for state_url, sp1 in fetchConcurrentList(states):
        cities = sp1.select("ul.Directory-listLinks a")
        if cities:
            for city_url, sp2 in fetchConcurrentList(cities):
                locations = sp2.select("ul.Directory-listTeasers h2 a")
                if locations:
                    for page_url, sp3 in fetchConcurrentList(locations):
                        yield _d(sp3, page_url)
                else:
                    yield _d(sp2, city_url)
        else:
            locs = sp1.select("ul.Directory-listTeasers h2 a")
            if locs:
                for url, sp4 in fetchConcurrentList(locs):
                    yield _d(sp4, url)
            else:
                yield _d(sp1, state_url)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
