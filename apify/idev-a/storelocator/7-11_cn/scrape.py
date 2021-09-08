from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import dirtyjson as json
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("7-11")

_headers = {
    "Host": "www.7-11.cn",
    "Accept": "text/html, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://www.7-11.cn",
    "Referer": "https://www.7-11.cn/ShopsNearby/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7-11.cn"
base_url = "https://www.7-11.cn/ajax/ajax.aspx"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(city):
    return city, request_with_retries(city["data"])


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


def request_with_retries(data):
    return session.post(base_url, headers=_headers, data=data)


def fetchConcurrentSingle1(city):
    return city, request_with_retries(city["data"])


def fetchConcurrentList1(list, occurrence=max_workers):
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


def request_with_retries1(data):
    return session.post(base_url, headers=_headers, json=data)


def fetch_data():
    data = {"act": "GetCity"}
    cities = [
        {"name": cc.text, "data": {"act": "GetCity", "ParentID": cc["value"]}}
        for cc in bs(request_with_retries(data).text, "lxml").select("option")
    ]
    for city, res in fetchConcurrentList(cities):
        areas = [
            {"name": cc.text, "data": {"act": "ShopScreening", "AreaID": cc["value"]}}
            for cc in bs(res.text, "lxml").select("option")
        ]
        for area, res1 in fetchConcurrentList1(areas):
            locations = bs(json.loads(res1.text)["html"], "lxml").select("tr")
            for _ in locations:
                bb = list(_.stripped_strings)
                addr = parse_address_intl("中国" + bb[1])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                yield SgRecord(
                    page_url=base_url,
                    location_name=bb[0],
                    street_address=street_address,
                    city=city["name"],
                    state=addr.state,
                    zip_postal=addr.postcode,
                    country_code="China",
                    locator_domain=locator_domain,
                    raw_address=bb[1],
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
