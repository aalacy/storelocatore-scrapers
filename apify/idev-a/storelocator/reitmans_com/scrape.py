from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("reitmans")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "if-none-match": 'W/"4375a-Jm/veTBrfVxN4XroCGUSdjj6B2U"',
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.reitmans.com/"
base_url = "https://locations.reitmans.com/en"

session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(_):
    page_url = "https://locations.reitmans.com/" + _["properties"]["slug"]
    response = request_with_retries(page_url)
    return page_url, _, bs(response.text, "lxml")


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
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('"FeatureCollection","features":')[1]
            .split('},"uiLocationsList"')[0]
            .strip()
        )
        logger.info(f"{len(locations)} found")
        for page_url, _, sp1 in fetchConcurrentList(locations):
            ss = json.loads(sp1.find("script", type="application/ld+json").string)
            hours = [
                f"{hh['dayOfWeek']}: {hh['opens']}-{hh['closes']}"
                for hh in ss["openingHoursSpecification"]
            ]
            yield SgRecord(
                page_url=page_url,
                store_number=_["properties"]["id"],
                location_name=_["properties"]["name"],
                street_address=sp1.select_one(
                    'span[itemprop="streetAddress"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="addressLocality"]').text.strip(),
                state=sp1.select_one('span[itemprop="addressRegion"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postalCode"]').text.strip(),
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                country_code=ss["address"]["addressCountry"],
                phone=ss["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
