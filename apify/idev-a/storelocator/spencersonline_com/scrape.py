import math
from concurrent.futures import ThreadPoolExecutor
import time
from sgrequests.sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from bs4 import BeautifulSoup as bs
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

DOMAIN = "spencersonline.com"
website = "https://stores.spencersonline.com"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}


log = sglog.SgLogSetup().get_logger("spencersonline")


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


max_workers = 8


def fetchConcurrentSingle(data):
    return data["url"]


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
                log.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url, http):
    return http.get(url, headers=headers)


def fetchStates(http):
    urls = []
    for state in bs(request_with_retries(website, http).text, "lxml").select(
        "ul.browse a"
    ):
        urls.append({"url": state["href"]})
    return urls


def fetchCities(obj, http):
    urls = []
    for url in fetchConcurrentList(obj):
        response = request_with_retries(url, http)
        for data in bs(response.text, "lxml").select("div.map-list-item a"):
            urls.append({"url": data["href"]})

    return urls


def fetchUrls(obj, http):
    urls = []
    for url in fetchConcurrentList(obj):
        response = request_with_retries(url, http)
        for data in bs(response.text, "lxml").select(
            "div.map-list-item div.map-list-item-header a"
        ):
            urls.append({"url": data["href"]})

    return urls


def fetchData():
    with SgRequests(proxy_country="us") as http:
        states = fetchStates(http)
        log.info(f"Total states = {len(states)}")

        city_urls = fetchCities(states, http)
        page_urls = fetchUrls(city_urls, http)

        log.info(f"{len(page_urls)} found")
        for page_url in fetchConcurrentList(page_urls):
            log.info(page_url)
            res = request_with_retries(page_url, http)
            sp1 = bs(res.text, "lxml")
            ss = json.loads(
                bs(res.text, "lxml").find("script", type="application/ld+json").string
            )
            hours = []
            for hh in sp1.select("div.map-list div.hours div.day-hour-row"):
                hours.append(
                    f"{hh.select_one('.daypart').text.strip()}: {''.join(hh.select_one('.time').stripped_strings)}"
                )
            for _ in ss:
                country_code = "US"
                if _["address"]["addressRegion"] in ca_provinces_codes:
                    country_code = "CA"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    store_number=page_url.split("-")[-1].split(".")[0].strip(),
                    page_url=page_url,
                    location_name=sp1.select_one("span.location-name").text.strip(),
                    street_address=_["address"]["streetAddress"],
                    city=_["address"]["addressLocality"],
                    zip_postal=_["address"]["postalCode"],
                    state=_["address"]["addressRegion"],
                    country_code=country_code,
                    phone=_["address"]["telephone"],
                    latitude=_["geo"]["latitude"],
                    longitude=_["geo"]["longitude"],
                    hours_of_operation="; ".join(hours),
                )


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"{end-start} seconds.")


if __name__ == "__main__":
    scrape()
