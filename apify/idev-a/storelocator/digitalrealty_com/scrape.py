from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("digitalrealty")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.digitalrealty.com/data-centers"
locator_domain = "https://www.digitalrealty.com"
session = SgRequests().requests_retry_session()
max_workers = 16


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetchConcurrentSingle(link):
    page_url = link["href"]
    if "/data-centers/" in page_url:
        if not page_url.startswith("http"):
            page_url = locator_domain + page_url
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
    return session.get(url, headers=_headers)


def _d(page_url, sp3):
    ss = list(
        sp3.select("main div.uk-margin-medium")[0].select("p")[-1].stripped_strings
    )
    location_name = sp3.select_one(
        'h1[data-uk-scrollspy-class="uk-animation-slide-left"]'
    ).text.strip()
    city_state = sp3.select_one(
        'h2[data-uk-scrollspy-class="uk-animation-slide-right"]'
    ).text.strip()
    raw_address = location_name + " " + city_state
    addr = parse_address_intl(raw_address)
    city = addr.city
    zip_postal = addr.postcode
    phone = ""
    if ss:
        phone = ss[-1]
        if not _p(phone):
            phone = ""
    if location_name == "VESTA Querétaro Industrial Park":
        city = city_state.split(",")[0]
        zip_postal = city_state.split(",")[1]
    return SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=location_name,
        state=addr.state,
        city=city,
        zip_postal=zip_postal,
        country_code=addr.country,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
    )


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    countries = soup.select("div.Footer > div > ul > li")[1].select("ul a")
    logger.info(f"{len(countries)} found")
    for country_url, sp1 in fetchConcurrentList(countries):
        states = sp1.select("main div.uk-section div.uk-container ul a")
        logger.info(f"{len(states)} found")
        for state_url, sp2 in fetchConcurrentList(states):
            links = sp2.select("main a.uk-link-reset")
            for page_url, sp3 in fetchConcurrentList(links):
                logger.info(page_url)
                yield _d(page_url, sp3)

        if not states:
            import pdb

            pdb.set_trace()
            states1 = sp1.select("main a.uk-link-reset")
            for url, sp4 in fetchConcurrentList(states1):
                links1 = sp4.select("main a.uk-link-reset")
                if not links1:
                    logger.info(url)
                    yield _d(url, sp4)
                else:
                    for url1, sp5 in fetchConcurrentList(links1):
                        logger.info(url1)
                        yield _d(url1, sp5)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
