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

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.cef.co.uk/stores/directory?page={}"
locator_domain = "https://www.cef.co.uk"

max_workers = 8
days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def fetchConcurrentSingle(link):
    page_url = link.a["href"]
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
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("ul#directory li.branch")
            if not links:
                break
            page += 1
            logger.info(f"{len(links)} found")
            for page_url, sp1 in fetchConcurrentList(links):
                logger.info(page_url)
                _ = json.loads(
                    sp1.find("script", type="application/ld+json").string.replace(
                        "&quot;", '"'
                    )
                )
                addr = _["address"]
                coord = (
                    sp1.select_one("a.branch-info__content-address-directions")["href"]
                    .split("&query=")[1]
                    .split(",")
                )
                hours = []
                temp = {}
                for hh in _["openingHours"]:
                    if hh.startswith("Ba"):
                        continue
                    hr = hh.split()
                    temp[hr[0]] = hr[1]

                for dd in days:
                    if dd in temp.keys():
                        hours.append(f"{dd}: {temp[dd]}")
                    else:
                        hours.append(f"{dd}: closed")

                street_address = addr["streetAddress"].replace("&amp", "&").strip()
                if street_address.endswith(","):
                    street_address = street_address[:-1]

                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=street_address,
                    city=addr["addressLocality"],
                    state=addr["addressRegion"],
                    zip_postal=addr["postalCode"],
                    country_code="UK",
                    phone=addr["telephone"],
                    locator_domain=locator_domain,
                    latitude=coord[0],
                    longitude=coord[1],
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
