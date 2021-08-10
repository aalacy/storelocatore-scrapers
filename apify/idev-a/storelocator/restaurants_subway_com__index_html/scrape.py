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

logger = SgLogSetup().get_logger("subway")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://restaurants.subway.com/index.html"
locator_domain = "https://restaurants.subway.com/"
session = SgRequests().requests_retry_session()
max_workers = 12


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link["href"].replace("../", ""))
    if "additional-locations" not in page_url:
        response = request_with_retries(page_url)
        return page_url, bs(response.text, "lxml")
    else:
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
    return session.get(url, headers=_headers)


def _d(page_url, sp1):
    street_address = sp1.select_one(".c-address-street-1").text.strip()
    if sp1.select_one(".c-address-street-2"):
        street_address += " " + sp1.select_one(".c-address-street-2").text.strip()
    zip_postal = state = city = phone = ""
    if sp1.select_one(".c-address-city"):
        city = sp1.select_one(".c-address-city").text.strip()
    if sp1.select_one(".c-address-postal-code"):
        zip_postal = sp1.select_one(".c-address-postal-code").text.strip()
    if sp1.select_one(".c-address-state"):
        state = sp1.select_one(".c-address-state").text.strip()
    if sp1.select_one("div.Core-col div#phone-main"):
        phone = sp1.select_one("div.Core-col div#phone-main").text.strip()
    hours = []
    if sp1.select("table.c-hours-details"):
        for hh in sp1.select("table.c-hours-details")[0].select("tbody tr"):
            hours.append(hh["content"])

    return SgRecord(
        page_url=page_url,
        location_name=list(sp1.select_one('h1[itemprop="name"]').stripped_strings)[-1],
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=sp1.select_one(".c-address-country-name").text.strip(),
        phone=phone,
        locator_domain=locator_domain,
        latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
        longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
        hours_of_operation="; ".join(hours).replace("–", "-"),
    )


def fetch_data():
    countries = bs(session.get(base_url, headers=_headers).text, "lxml").select(
        "ul.Directory-listLinks a"
    )
    logger.info(f"{len(countries)} found")
    for country_url, sp1 in fetchConcurrentList(countries):
        states = sp1.select("ul.Directory-listLinks a")
        for state_url, sp2 in fetchConcurrentList(states):
            cities = sp2.select("ul.Directory-listLinks a")
            if cities:
                for city_url, sp3 in fetchConcurrentList(cities):
                    loc1s = sp3.select("ul.Directory-listTeasers a")
                    if loc1s:
                        for page_url1, sp5 in fetchConcurrentList(loc1s):
                            yield _d(page_url1, sp5)
                    else:
                        yield _d(city_url, sp3)
            else:
                locs = sp2.select("ul.Directory-listTeasers a")
                if locs:
                    for page_url, sp4 in fetchConcurrentList(locs):
                        yield _d(page_url, sp4)
                else:
                    yield _d(state_url, sp2)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
