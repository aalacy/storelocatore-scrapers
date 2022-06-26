from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.kfc.com.sg/Location/Search"
locator_domain = "https://www.kfc.com.sg"
session = SgRequests().requests_retry_session()
max_workers = 8

data = {
    "DeliveryAddressInformation": {
        "City": "",
        "StateCode": "",
        "State": "",
        "Comments": "",
    },
    "RestaurantSearchKeyword": "",
    "OrderReadyDateTime": "",
    "SearchedLocationGeoCode": {
        "DeliveryAddress": {"City": "", "StateCode": "", "Comments": ""},
        "Latitude": "null",
        "Longitude": "null",
    },
    "SelectedRestaurantId": "119",
    "topOneStore": "false",
    "IsAllKFC": "false",
    "isShowOrderButton": "true",
}


def fetchConcurrentSingle(link):
    page_url = "https://www.kfc.com.sg/KFCLocation/StoreDetails"
    data["SelectedRestaurantId"] = link["data-restaurantid"]
    response = session.post(page_url, headers=header1, json=data).json()
    return link, bs(response["DataObject"], "lxml")


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


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div.restaurantDetails")
    logger.info(f"{len(links)} found")
    for _, sp1 in fetchConcurrentList(links):
        hours = [
            ": ".join(hh.stripped_strings)
            for hh in sp1.select("div.store__open-hours table tr")
        ]
        if not _["data-isrestaurantopen"]:
            continue
        street_address = _["data-address-street"].replace("Singapore", "").strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        yield SgRecord(
            page_url=base_url,
            store_number=_["data-restaurantid"],
            location_name=_["data-restaurantname"],
            street_address=street_address,
            city=_.get("data-address-city"),
            state=_.get("data-address-state"),
            zip_postal=_["data-address-pincode"],
            country_code="Singapore",
            phone=_["data-phoneno"],
            locator_domain=locator_domain,
            latitude=_["data-latitude"],
            longitude=_["data-longitude"],
            hours_of_operation="; ".join(hours).replace("–", "-"),
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
