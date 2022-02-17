from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from datetime import datetime

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.lebanon.kfc.me/WebAPI/v2/Location/States?DeliveryMode=H"
locator_domain = "https://www.lebanon.kfc.me"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(city):
    now = datetime.now().strftime("%m/%d/%Y")
    page_url = f"https://www.lebanon.kfc.me/WebAPI/Location/Search?Channel=W&deliverymode=H&date={now}&city={city['CityId']}&filters=deliverymode-date-slot-city&Format=html&CurrentEvent=Location_Search"
    response = request_with_retries(page_url)
    return (
        page_url,
        city,
        bs(
            response.text[1:-1]
            .strip()
            .replace("\\r\\n", "")
            .replace('\\"', "")
            .replace('"', ""),
            "lxml",
        ),
    )


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


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    states = session.get(base_url, headers=_headers).json()["data"]["states"]
    logger.info(f"{len(states)} states found")
    for state in states:
        area_url = f"https://www.lebanon.kfc.me/WebAPI/v2/Location/State/{state['StateCode']}/Cities"
        cities = session.get(area_url, headers=_headers).json()["data"]["CityList"]
        logger.info(f"[{state['StateName']}] {len(cities)} cities found")
        for page_url, city, sp2 in fetchConcurrentList(cities):
            for _ in sp2.select("div.store-list"):
                hours = list(_.select_one("div.store-time").stripped_strings)
                phone = ""
                if hours:
                    del hours[0]
                    if _p(hours[-1]):
                        phone = hours[-1]
                        del hours[-1]

                yield SgRecord(
                    page_url=page_url,
                    store_number=_.select_one(".store-selectionbtn")["data-location"],
                    location_name=_.select_one(".store-name").text.strip(),
                    street_address=_.select_one(".store-address").text.strip(),
                    city=city["CityName"],
                    state=state["StateName"],
                    country_code="Lebanon",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="".join(hours).replace("–", "-"),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
