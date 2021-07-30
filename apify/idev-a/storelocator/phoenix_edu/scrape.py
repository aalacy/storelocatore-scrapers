from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("phoenix")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.phoenix.edu"
base_url = "https://www.phoenix.edu/api/plct/3/uopx/locations?type=site&page.size=100"

session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(loc):
    page_url = loc["attributes"]["ref"]
    response = request_with_retries(page_url)
    return loc, response


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
    locations = session.get(base_url, headers=_headers).json()["results"]
    for loc, res in fetchConcurrentList(locations):
        logger.info(res.url)
        hours_of_operation = ""
        sp1 = bs(res.text, "lxml")
        if res.url != "https://www.phoenix.edu/campus-locations.html":
            if sp1.select_one("div.tabindexClass"):
                if "temporarily closed" in sp1.select_one("div.tabindexClass").text:
                    hours_of_operation = "temporarily closed"
                else:
                    hours_of_operation = (
                        sp1.select("div.tabindexClass p")[-1]
                        .text.replace("&amp;", "&")
                        .replace("\xa0", " ")
                    )
                    if "hours" not in hours_of_operation.lower():
                        hours_of_operation = ""
                    else:
                        hours_of_operation = hours_of_operation.replace("Hours:", "")
            elif sp1.select_one("div.react-campusdetailhero-container"):
                ss = json.loads(
                    sp1.select_one("div.react-campusdetailhero-container")[
                        "data-json-properties"
                    ]
                    .replace("&#34;", '"')
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                )
                if ss["campusData"].get("hours"):
                    hours_of_operation = "; ".join(
                        bs(ss["campusData"]["hours"], "lxml").stripped_strings
                    )
                    if "temporarily closed" in hours_of_operation:
                        hours_of_operation = "temporarily closed"

        _ = loc["attributes"]
        street_address = _["addressLine2"]
        if _.get("addressLine3"):
            street_address += " " + _["addressLine3"]
        phone = _.get("phoneLocal")
        if not phone:
            phone = _.get("phoneTollFree")
        yield SgRecord(
            page_url=res.url,
            location_name=_["altName"],
            street_address=street_address,
            city=_["city"],
            state=_["stateProvince"],
            zip_postal=_["postalCode"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            country_code=loc["countryCode"],
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
