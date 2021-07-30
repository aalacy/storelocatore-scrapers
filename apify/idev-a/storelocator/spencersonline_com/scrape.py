import math
from concurrent.futures import ThreadPoolExecutor
import time
import os
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from bs4 import BeautifulSoup as bs
import us
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

DOMAIN = "spencersonline.com"
website = "https://stores.spencersonline.com"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}
DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "https://": proxy_url,
        }
        return proxies
    else:
        return None


session = SgRequests(proxy_rotation_failure_threshold=20).requests_retry_session()
session.proxies = set_proxies()
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


max_workers = 12


def fetchConcurrentSingle(data):
    response = request_with_retries(data["url"])
    return data["url"], response.text


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


def request_with_retries(url):
    return session.get(url, headers=headers)


def fetchStates():
    urls = []
    for state in us.states.STATES:
        urls.append({"url": f"{website}/{state.name}"})
    return urls


def fetchUrls(obj):
    urls = []
    for url, response in fetchConcurrentList(obj):
        response = request_with_retries(url)
        data = json.loads(
            response.text.split('"markerData":')[1].split("</script>")[0].strip()[:-2]
        )
        for el in data:
            urls.append({"url": json.loads(bs(el["info"], "lxml").text)["url"]})

    return urls


def fetchData():
    states = fetchStates()
    log.info(f"Total states = {len(states)}")

    urls = fetchUrls(states)
    city_urls = fetchUrls(urls)
    page_urls = fetchUrls(city_urls)

    log.info(f"{len(page_urls)} found")
    for page_url, response in fetchConcurrentList(page_urls):
        log.info(page_url)
        res = request_with_retries(page_url)
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


session.close()
if __name__ == "__main__":
    scrape()
