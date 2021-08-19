from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfc.co.jp/"
base_url = "https://search.kfc.co.jp/api/point?f=%5B%22%E9%83%B5%E4%BE%BF%E7%95%AA%E5%8F%B7%22,%22%E3%83%87%E3%83%AA%E3%83%90%E3%83%AA%E3%83%BC%E3%82%A8%E3%83%AA%E3%82%A2%22,%22%E3%83%87%E3%83%AA%E3%83%90%E3%83%AA%E3%83%BC%E3%82%A8%E3%83%AA%E3%82%A2%EF%BC%92%22,%22%E3%83%87%E3%83%AA%E3%83%90%E3%83%AA%E3%83%BC%E3%82%A8%E3%83%AA%E3%82%A2%EF%BC%93%22%5D&np=%7B%7D&v=527.1"

session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(page_url):
    response = request_with_retries(page_url)
    return page_url, json.loads(
        response.text.split("constant('CURRENT_POINT',")[1]
        .split(".constant(")[0]
        .strip()[:-1]
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
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    locations = session.get(base_url, headers=_headers).json()["items"]
    urls = []
    for _ in locations:
        urls.append(f"https://search.kfc.co.jp/map/{_['key']}")
    for page_url, _ in fetchConcurrentList(urls):
        hours = []
        if _["平日営業時間"]:
            hours.append(_["平日営業時間"])
        if _["土日祝営業時間"]:
            hours.append(_["土日祝営業時間"])
        yield SgRecord(
            page_url=page_url,
            store_number=_["key"],
            location_name=_["name"],
            street_address=_["address"],
            zip_postal=_["郵便番号"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            country_code="JP",
            phone=_["tel"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=_["address"],
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
