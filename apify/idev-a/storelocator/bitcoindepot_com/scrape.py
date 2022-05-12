from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl

import json
import math
from concurrent.futures import ThreadPoolExecutor

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
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
loc_url = "https://bitcoindepot.com/get-map-points/"

max_workers = 1


def fetchConcurrentSingle(loc, locations):
    page_url = locator_domain + loc["href"]
    _i = list(loc.stripped_strings)
    raw_address = ", ".join(_i[1].split(",")[2:])
    if _i[0] not in raw_address:
        raw_address += " " + _i[0]
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += " " + addr.street_address_2
    store = dict(
        hours_of_operation=loc.select_one("span.list-country-list-time").text.strip(),
        name=_i[1].split(",")[1].strip(),
        address=street_address,
        city=_i[0],
        state=addr.state or "",
        zip_postal=addr.postcode or "",
    )
    logger.info(page_url)
    try:
        res = request_with_retries(page_url)
        if res.status_code != 200:
            return page_url, store
        loc = json.loads(
            bs(res.text, "lxml").find("script", type="application/ld+json").string
        )
        data = {"location_group": loc["url"]}
        _ = http.post(loc_url, headers=_headers, data=data).json()["set_locations"][0]
    except:
        logger.info("=========== exception")
        _ = _loc(locations, store)
        page_url = base_url

    return page_url, _


def fetchConcurrentList(list, locations, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(
            fetchConcurrentSingle, list, [locations] * len(list)
        ):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


def _loc(locations, store):
    for loc in locations:
        if loc["name"] == store["name"] and loc["city"] == store["city"]:
            return loc
    return None


def fetch_records(http):
    res = http.get(base_url)
    header1["x-csrftoken"] = res.cookies.get("csrftoken")
    locs = bs(res.text, "lxml").select(
        "li.list-country-list-item > a.list-country-list-link"
    )
    locations = http.post(loc_url, headers=header1).json()["set_locations"]
    for page_url, _ in fetchConcurrentList(locs, locations):
        hours_of_operation = ""
        if _.get("hours"):
            hours_of_operation = (
                _["hours"]
                .replace("\n", "; ")
                .replace("\r", "")
                .replace("\t", " ")
                .replace("–", "-")
                .strip()
                .replace(",", "; ")
                .replace("Unknown", "")
                .strip()
            )
        else:
            hours_of_operation = _.get("hours_of_operation")

        country_code = "US"
        if _["state"] in ca_provinces_codes:
            country_code = "CA"
        if hours_of_operation and hours_of_operation.strip().endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

        zip_postal = _["zip"]
        if zip_postal:
            zip_postal = zip_postal.replace("Canada", "").replace(",", "").strip()
        yield SgRecord(
            page_url=page_url,
            location_name=_["name"],
            street_address=_["address"].replace(",", ""),
            city=_["city"],
            state=_["state"],
            zip_postal=zip_postal,
            location_type=_.get("type"),
            latitude=_.get("lat"),
            longitude=_.get("lng"),
            country_code=country_code,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
