from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("pizzahut")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.pizzahut.ae/api/states?pageSize=1000&pageOffset=0&deliveryMode=H&langCode=en"
city_url = "https://www.pizzahut.ae/api/states/{}/cities?pageSize=1000&pageOffset=0&sort-order=ASC&deliveryMode=H&langCode=en"
locator_domain = "https://www.pizzahut.ae"
session = SgRequests().requests_retry_session()
max_workers = 12


def fetchConcurrentSingle(city):
    page_url = f"https://www.pizzahut.ae/api//cities/{city['id']}/stores?deliveryMode=H&langCode=en"
    locs = request_with_retries(page_url).json()["body"]
    return locs, city


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


def fetch_data():
    states = session.get(base_url, headers=_headers).json()["body"]
    for state in states:
        cities = session.get(city_url.format(state["code"]), headers=_headers).json()[
            "body"
        ]
        logger.info(f"[{state['name']}] {len(cities)} cities found")
        for locs, city in fetchConcurrentList(cities):
            for _ in locs:
                raw_address = _["address"].strip()
                if (
                    "UAE" not in raw_address
                    and "United Arab Emirates" not in raw_address
                ):
                    raw_address += ", United Arab Emirates"
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = _["city"]["name"]
                if not city and addr.city:
                    city = addr.city
                yield SgRecord(
                    page_url="",
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=city,
                    state=state["name"],
                    country_code="UAE",
                    phone=_["contactNo"],
                    latitude=_["locationDetail"]["latitude"],
                    longitude=_["locationDetail"]["longitude"],
                    locator_domain=locator_domain,
                    raw_address=_["address"].strip(),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
