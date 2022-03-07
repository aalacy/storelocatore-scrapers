import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.specsavers.co.uk"
base_url = "https://www.specsavers.co.uk/stores/full-store-list"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


max_workers = 1


def fetchConcurrentSingle(link):
    page_url = "https://www.specsavers.co.uk/stores/" + link["href"]
    response = request_with_retries(page_url)
    return page_url, bs(response.text, "lxml")


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
    with SgRequests(proxy_country="us") as session:
        logger.info(url)
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        store_links = soup.select("div.item-list ul li a")
        for page_url, soup in fetchConcurrentList(store_links):
            detail_url = soup.find(
                "script", src=re.compile(r"https://knowledgetags.yextpages.net")
            )["src"].replace("&amp;", "&")
            res2 = session.get(detail_url)
            _ = json.loads(res2.text.split("Yext._embed(")[1].strip()[:-1])["entities"][
                0
            ]["attributes"]
            location_type = "Hearing Centre" if "hearing" in page_url else "Optician"
            if _.get("yextDisplayLat"):
                latitude = _["yextDisplayLat"]
                longitude = _["yextDisplayLng"]
            else:
                latitude = _["displayLat"]
                longitude = _["displayLng"]
            yield SgRecord(
                page_url=_["websiteUrl"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                phone=_["phone"],
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation="; ".join(_["hours"]),
                location_type=location_type,
                country_code=_["countryCode"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
