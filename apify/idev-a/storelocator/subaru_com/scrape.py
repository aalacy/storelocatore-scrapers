from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import ssl
import math
from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

session = SgRequests().requests_retry_session()
logger = SgLogSetup().get_logger("subaru")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.subaru.com/"
base_url = "https://www.subaru.com/services/dealers/distances/by/bounded-location?latitude=39.857117&longitude=-98.56977&neLatitude=84.92891450547761&neLongitude=180&swLatitude=-20.626499923373608&swLongitude=-180&count=-1"


max_workers = 8


def fetchConcurrentSingle(loc):
    _ = loc["dealer"]
    if _["siteUrl"] != "https://null":
        try:
            response = request_with_retries(_["siteUrl"])
            return _["siteUrl"], _, bs(response.text, "lxml")
        except:
            return _["siteUrl"], _, ""


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
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for page_url, _, sp1 in fetchConcurrentList(locations):
            if not sp1:
                continue
            street_address = _["address"]["street"]
            if _["address"]["street2"]:
                street_address += " " + _["address"]["street2"]
            logger.info(page_url)
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div#hours1-app-root li")
            ]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=_["address"]["city"],
                state=_["address"]["state"],
                zip_postal=_["address"]["zipcode"],
                latitude=_["location"]["latitude"],
                longitude=_["location"]["longitude"],
                country_code="US",
                phone=_["phoneNumber"].strip(),
                location_type=_["address"]["type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
