from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("moes")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.nisalocally.co.uk/stores/index.html"
locator_domain = "https://www.nisalocally.co.uk/"
session = SgRequests()
max_workers = 12


def fetchConcurrentSingle(link):
    page_url = link["href"].replace(".", "").replace("..", "")
    if not page_url.startswith("/"):
        page_url = "/" + page_url
    if not page_url.startswith("http"):
        page_url = "https://www.nisalocally.co.uk/stores" + page_url
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
    logger.info(page_url)
    street_address = sp1.select_one('meta[itemprop="streetAddress"]')["content"].strip()
    if street_address.endswith(","):
        street_address = street_address[:1]
    location_name = sp1.select_one("span#location-name .LocationName-geo").text.strip()
    if location_name.endswith(","):
        location_name = location_name[:-1]
    hours = [hh["content"] for hh in sp1.select("table.c-hours-details tbody tr")]
    phone = ""
    if sp1.select_one("div#phone-main"):
        phone = sp1.select_one("div#phone-main").text.strip()
    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=sp1.select_one('meta[itemprop="addressLocality"]')["content"],
        zip_postal=sp1.select_one(".c-address-postal-code").text.strip(),
        country_code="uk",
        phone=phone,
        latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
        longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours).replace("–", "-"),
    )


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    states = soup.select("ul.Directory-listLinks a")
    total = 0
    for state in states:
        total += int(state["data-count"][1:-1])
    logger.info(f"total {total} locations")
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
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

    del session
