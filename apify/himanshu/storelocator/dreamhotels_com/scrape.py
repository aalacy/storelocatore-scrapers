import json

from bs4 import BeautifulSoup as bs

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


DOMAIN = "dreamhotels.com"
BASE_URL = "https://www.dreamhotels.com/"
LOCATION_URL = "https://www.dreamhotels.com/destinations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    links = soup.find_all("div", {"class": "m-content-object__content"})
    for i in links:
        link = i.a["href"]
        if "http" not in link:
            link = "https://www.dreamhotels.com" + i.a["href"]
        store_urls.append(link)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data(sgw: SgWriter):
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locator_domain = DOMAIN
    for page_url in page_urls:
        soup = pull_content(page_url)
        store = json.loads(
            soup.find_all("script", attrs={"type": "application/ld+json"})[-1].contents[
                0
            ]
        )
        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = store["address"]["addressCountry"]
        if "States" not in country_code:
            continue
        phone = soup.find(class_="page-footer__contact").p.a.text
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store["hasMap"].split("=")[-1].split(",")[0].strip()
        longitude = store["hasMap"].split("=")[-1].split(",")[1].strip()
        log.info("Append {} => {}".format(location_name, street_address))

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
