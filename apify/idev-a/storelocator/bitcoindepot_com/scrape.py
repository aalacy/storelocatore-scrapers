from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bitcoindepot")

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://bitcoindepot.com",
    "referer": "https://bitcoindepot.com/locations/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://bitcoindepot.com"
base_url = "https://bitcoindepot.com/locations/"
map_url = "https://bitcoindepot.com/get-map-points/"
session = SgRequests().requests_retry_session()
max_workers = 24


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link["href"])
    data = {"location_group": link["href"].split("/")[-1]}
    response = session.post(map_url, headers=header1, data=data).json()["set_locations"]
    return page_url, response


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
    res = session.get(base_url, headers=_headers)
    header1["x-csrftoken"] = res.cookies.get_dict()["csrftoken"]
    links = bs(res.text, "lxml").select("a.list-country-list-link")
    logger.info(f"{len(links)} found")
    for page_url, locations in fetchConcurrentList(links):
        logger.info(page_url)
        for _ in locations:
            hours_of_operation = ""
            if _.get("hours"):
                hours_of_operation = (
                    _["hours"]
                    .replace("\r\n", "; ")
                    .replace("–", "-")
                    .strip()
                    .replace(",", "; ")
                    .replace("Unknown", "")
                )

            country_code = "US"
            if _["state"] in ca_provinces_codes:
                country_code = "CA"
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"].replace(",", ""),
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                location_type=_["type"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=country_code,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
