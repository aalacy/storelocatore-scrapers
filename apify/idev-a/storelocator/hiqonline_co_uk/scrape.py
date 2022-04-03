from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("hiqonline")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.hiqonline.co.uk/hiq-centres"
locator_domain = "https://www.hiqonline.co.uk"
session = SgRequests()
max_workers = 8
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetchConcurrentSingle(link):
    page_url = link["href"]
    if not page_url.startswith("http"):
        page_url = locator_domain + link["href"]
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
    return session.get(url, headers=_headers)


def _dd(page_url, _, loc, city):
    logger.info(page_url)
    state = ""
    if _.select_one('span[itemprop="addressRegion"]'):
        state = _.select_one('span[itemprop="addressRegion"]').text.strip()
    temp = list(_.select("div.details ul li")[-1].stripped_strings)
    hours = []
    for x in range(0, len(temp), 2):
        hours.append(f"{temp[x]} {temp[x+1]}")
    if not hours:
        for day in days:
            hours.append(f"{day}: closed")
    coord = loc.select_one(".address")["data-lat-long"].split(",")
    raw_address = (
        " ".join(_.select_one('li[itemprop="address"]').stripped_strings)
        .replace("\n", " ")
        .strip()
    )
    return SgRecord(
        page_url=page_url,
        location_name=_.h3.text.strip(),
        street_address=_.select_one('span[itemprop="streetAddress"]').text.strip(),
        city=_.select_one('span[itemprop="addressLocality"]').text.strip(),
        state=state,
        zip_postal=_.select_one('span[itemprop="postalCode"]').text.strip(),
        country_code="UK",
        phone=_.select_one('span[itemprop="telephone"]').text.strip(),
        locator_domain=locator_domain,
        latitude=coord[0],
        longitude=coord[1],
        hours_of_operation="; ".join(hours).replace("–", "-"),
        raw_address=raw_address,
    )


def _d(page_url, _, city):
    logger.info(page_url)
    raw_address = ", ".join(
        _.select_one(".address").text.strip().split(",")[1:]
    ).strip()
    if "United Kingdom" not in raw_address:
        raw_address += ", United Kingdom"
    coord = _.select_one(".address")["data-lat-long"].split(",")
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    zip_postal = addr.postcode
    if zip_postal and len(zip_postal.split(" ")) == 1:
        for aa in raw_address.split(","):
            if zip_postal.lower() in aa.lower():
                zip_postal = aa.strip()
                break
    temp = list(_.select_one("div.opening").stripped_strings)
    hours = []
    for x in range(0, len(temp), 2):
        hours.append(f"{temp[x]} {temp[x+1]}")
    return SgRecord(
        page_url=page_url,
        location_name=_.h3.text.strip(),
        street_address=street_address,
        city=city.text.split("(")[0].strip(),
        state=addr.state,
        zip_postal=zip_postal,
        country_code="UK",
        phone=_.select_one("a.tel").text.strip(),
        locator_domain=locator_domain,
        latitude=coord[0],
        longitude=coord[1],
        hours_of_operation="; ".join(hours).replace("–", "-"),
        raw_address=raw_address,
    )


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div.cities-list ul a")
    logger.info(f"{len(links)} found")
    for city_url, city, sp1 in fetchConcurrentList(links):
        locations = sp1.select("div.result-container")
        locs = sp1.select("ul#locations li")
        for x, _ in enumerate(locations):
            yield _dd(_.select_one("a.btn")["href"], _, locs[x], city)
        if not locations:
            yield _d(city_url, sp1, city)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
