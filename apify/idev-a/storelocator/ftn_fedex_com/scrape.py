from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("fedex")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://ftn.fedex.com"
base_url = "https://local.fedex.com/en"
json_url = "https://local.fedex.com/en/search?entityId={}"
locator = "https://local.fedex.com/"


max_workers = 16


def fetchConcurrentSingle(loc, url):
    page_url = urljoin(url, loc.a["href"])
    logger.info(page_url)
    if loc.select_one("div.js-hours-today-teaser-placeholder"):
        entity_id = loc.select_one("div.js-hours-today-teaser-placeholder")[
            "data-entity-id"
        ]
    else:
        entity_id = page_url.split("/")[-1]
    rr_url = request_with_retries(json_url.format(entity_id))
    if rr_url.status_code != 200:
        return None
    res = rr_url.json()
    if res.get("errors"):
        return None
    store = res["response"]["entities"][0]
    return store, page_url


def fetchConcurrentList(list, url, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list, len(list) * [url]):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def fetchConcurrentItem(loc, url):
    dir_url = urljoin(url, loc["href"])
    logger.info(f"{dir_url}")
    rr_dir = request_with_retries(dir_url)
    if rr_dir.status_code != 200:
        return None
    return bs(rr_dir.text, "lxml"), dir_url, loc


def fetchConcurrentItems(list, url, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentItem, list, len(list) * [url]):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=header1)


def _time(val):
    val = str(val)
    if len(val) == 3:
        val = "0" + val
    return val[:2] + ":" + val[2:]


def _d(store, page_url):
    _ = store["profile"]
    addr = _["address"]
    street_address = addr["line1"]
    if addr.get("line2"):
        street_address += " " + addr.get("line2")
    if addr.get("line3"):
        street_address += " " + addr.get("line3")

    street_address = (
        street_address.replace("\n", " ").replace("\t", "").replace("\r", "")
    )
    if street_address == "None":
        street_address = ""

    city = addr["city"]
    state = addr.get("region")
    country_code = addr.get("countryCode")
    if country_code in ["JP", "CN"]:
        if city:
            street_address = street_address.replace(city, "")
        if state:
            street_address = street_address.replace(state, "")
        if street_address.startswith("市"):
            street_address = street_address[1:]
    if country_code == "KR":
        _st = street_address.split()
        if _st[-1].endswith("도"):
            if not state:
                state = _st[-1]
            del _st[-1]
        if _st[0] == city:
            del _st[0]

        street_address = " ".join(_st)

    lat = lng = ""
    if _.get("geocodedCoordinate"):
        lat = _["geocodedCoordinate"]["lat"]
        lng = _["geocodedCoordinate"]["long"]
    elif _.get("yextDisplayCoordinate"):
        lat = _["yextDisplayCoordinate"]["lat"]
        lng = _["yextDisplayCoordinate"]["long"]
    hours = []
    if _.get("hours") and _["hours"].get("normalHours", []):
        for hh in _["hours"]["normalHours"]:
            times = []
            if hh["isClosed"]:
                times = ["Closed"]
            if not hh["isClosed"]:
                for interval in hh["intervals"]:
                    times.append(
                        f"{_time(interval['start'])} - {_time(interval['end'])}"
                    )
            hours.append(f"{hh['day']}: {', '.join(times)}")
    return SgRecord(
        page_url=page_url,
        location_name=_["name"],
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=addr.get("postalCode"),
        latitude=lat,
        longitude=lng,
        phone=_.get("mainPhone", {}).get("display"),
        country_code=country_code,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    with SgRequests() as http:
        country_blocks = bs(http.get(base_url, headers=_headers).text, "lxml").select(
            "ul.Directory-listLinks.Directory-countrySection"
        )
        for country_block in country_blocks:
            country_links = country_block.select("a")
            for country_bs, country_url, country_link in fetchConcurrentItems(
                country_links, locator
            ):
                dir_items = country_bs.select("ul.Directory-listLinks li a")
                for rr_bs, dir_url, dir_link in fetchConcurrentItems(
                    dir_items, country_url
                ):
                    sec_dir_items = rr_bs.select("ul.Directory-listLinks li a")
                    if not sec_dir_items:
                        # look for location items
                        locations = rr_bs.select("ul.Directory-listTeasers li")
                        logger.info(f"[{country_link.text}] found: {len(locations)}")
                        for store, page_url in fetchConcurrentList(locations, dir_url):
                            yield _d(store, page_url)
                    else:
                        for (
                            sec_rr_bs,
                            sec_dir_url,
                            sec_dir_link,
                        ) in fetchConcurrentItems(sec_dir_items, country_url):
                            locations = sec_rr_bs.select("ul.Directory-listTeasers li")
                            logger.info(
                                f"[{country_link.text}] found: {len(locations)}"
                            )
                            for store, page_url in fetchConcurrentList(
                                locations, sec_dir_url
                            ):
                                yield _d(store, page_url)


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        for rec in fetch_data():
            if rec:
                writer.write_row(rec)
