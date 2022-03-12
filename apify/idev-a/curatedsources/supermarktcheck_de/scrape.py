import dirtyjson as json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


locator_domain = "https://www.supermarktcheck.de"
base_url = "https://www.supermarktcheck.de/supermaerkte/"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


max_workers = 24


def fetchConcurrentSingle(link):
    page_url = locator_domain + link.a["href"]
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
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container.indexListContainer a")
        logger.info(f"{len(links)} found")
        for link in links:
            city_url = locator_domain + link["href"]
            logger.info(city_url)
            page = 1
            while True:
                with SgRequests(proxy_country="us") as http:
                    locations = bs(
                        http.get(f"{city_url}?page={page}", headers=_headers).text,
                        "lxml",
                    ).select("div.supermarketListElement")
                    logger.info(f"page {page}, {len(locations)}")
                    if not locations:
                        break
                    page += 1
                    for page_url, sp2 in fetchConcurrentList(locations):
                        raw_address = " ".join(
                            list(sp2.select_one("div.card-body p").stripped_strings)
                        )
                        hours = []
                        for hh in sp2.select("section#oeffnungszeiten table tr"):
                            td = list(hh.stripped_strings)
                            hours.append(f"{td[0]}: {td[1]}")
                        phone = list(sp2.select("div.card-body p")[1].stripped_strings)[
                            -1
                        ]
                        _ = json.loads(
                            sp2.select_one('script[type="application/ld+json"]').text
                        )
                        addr = _["address"]
                        city = addr["addressLocality"]
                        if city:
                            city = city.split("/")[0]
                        yield SgRecord(
                            page_url=page_url,
                            location_name=_["name"],
                            street_address=addr["streetAddress"],
                            city=city,
                            zip_postal=addr["postalCode"],
                            country_code="DE",
                            phone=_p(phone),
                            locator_domain=locator_domain,
                            latitude=_["geo"]["latitude"],
                            longitude=_["geo"]["longitude"],
                            hours_of_operation="; ".join(hours).replace("–", "-"),
                            raw_address=raw_address,
                        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
