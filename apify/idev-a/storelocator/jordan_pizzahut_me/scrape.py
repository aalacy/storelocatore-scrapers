from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("pizzahut")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = (
    "https://www.jordan.pizzahut.me/WebAPI/Location/State/JO2/Cities?DeliveryMode=S"
)
locator_domain = "https://www.jordan.pizzahut.me"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(city):
    page_url = f"https://www.jordan.pizzahut.me/WebAPI/Location/Search?Channel=W&deliverymode=S&city={city['CityId']}&ignoreslot=1&Currpage=1&Pagesize=5&TemplateId=123&searchby=city&filters=deliverymode-block-dinein-city&Format=html&CurrentEvent=Location_Search"
    response = request_with_retries(page_url)
    return (
        city,
        bs(
            response.text[1:-1]
            .strip()
            .replace("\\r\\n", "")
            .replace("\\t", "")
            .replace('\\"', ""),
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


def fetch_data():
    cities = json.loads(session.get(base_url, headers=_headers).json()["CityList"])
    logger.info(f"{len(cities)} cities found")
    for city, sp1 in fetchConcurrentList(cities):
        for _ in sp1.select("li.storename"):
            page_url = _.a["href"]
            if not page_url.startswith("http"):
                page_url = "https:" + _.a["href"]
            logger.info(page_url)
            sp2 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp2.select("table.store-hours tr")
            ]
            phone = list(sp1.select_one("div.store-phone").stripped_strings)[-1]
            if hours:
                del hours[0]
            addr = list(sp1.select_one("div.store-address").stripped_strings)
            coord = sp2.select_one("div.contact-info a")
            latitude = coord["data-lati"]
            longitude = coord["data-long"]
            if float(latitude) == 0.0:
                latitude = ""
            if float(longitude) == 0.0:
                longitude = ""
            yield SgRecord(
                page_url=page_url,
                store_number=page_url.split("LocId=")[-1],
                location_name=addr[0],
                street_address=addr[1],
                city=city["CityName"],
                country_code="Jordan",
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
