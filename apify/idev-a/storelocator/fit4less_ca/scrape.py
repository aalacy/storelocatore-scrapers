from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import math
from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("fit4less")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

session = SgRequests().requests_retry_session()


max_workers = 8


def fetchConcurrentSingle(data):
    response = request_with_retries(data)
    return data, response.text


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
    locator_domain = "https://www.fit4less.ca"
    base_url = "https://www.fit4less.ca/memberships/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div#city-dropdown ul li")
        logger.info(f"{len(links)} found")
        urls = []
        for link in links:
            url = f"https://www.fit4less.ca/locations/provinces/{link['data-provname'].replace('.','').replace(' ','-')}/{link['data-cityname'].replace('.','').replace(' ','-')}"
            sp1 = bs(session.get(url, headers=_headers).text, "lxml")
            locations = sp1.select("div#LocationResults div.find-gym__result")
            logger.info(
                f"[{link['data-provname']}, {link['data-cityname']}] {len(locations)} found"
            )
            for _ in locations:
                urls.append(locator_domain + _.a["href"])

        for page_url, res in fetchConcurrentList(urls):
            logger.info(page_url)
            sp2 = bs(res, "lxml")
            hours = []
            temp = list(
                sp2.select_one(
                    "div.hours-of-operation span.hours-hours"
                ).stripped_strings
            )
            if temp and "coming soon" in temp[0].lower():
                continue
            if temp and "closed" in temp[0].lower():
                hours = ["closed"]
            else:
                for x in range(0, len(temp), 2):
                    hours.append(f"{temp[x]} {temp[x+1]}")
            ss = json.loads(sp2.find("script", type="application/ld+json").string)
            yield SgRecord(
                page_url=page_url,
                location_name=ss["name"],
                street_address=ss["address"]["streetAddress"],
                city=ss["address"]["addressLocality"],
                state=ss["address"]["addressRegion"],
                zip_postal=ss["address"]["postalCode"],
                country_code=ss["address"]["addressCountry"],
                phone=ss["telephone"],
                locator_domain=locator_domain,
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
