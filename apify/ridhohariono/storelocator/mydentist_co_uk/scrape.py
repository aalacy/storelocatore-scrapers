from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "mydentist.co.uk"
BASE_URL = "https://www.mydentist.co.uk"
LOCATION_URL = "https://www.mydentist.co.uk/dentists"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_store_url():
    soup = pull_content(LOCATION_URL)
    store_urls = []
    parent_urls = soup.select("div#dentist-list-wrapper ul li a")
    for parent in parent_urls:
        parent_url = BASE_URL + parent["href"]
        contents = pull_content(parent_url)
        child_urls = contents.select("ul.fad-list a")
        for child in child_urls:
            child_url = "/".join(parent_url.split("/")[:-1]) + "/" + child["href"]
            stores = pull_content(child_url)
            child_urls = stores.select("ul.fad-list.fad-practices a")
            for url in child_urls:
                store_urls.append(BASE_URL + url["href"])
    log.info(f"Found {len(store_urls)} store urls")
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    urls = get_store_url()
    for page_url in urls:
        if "61-high-street-0" in page_url:
            continue
        store = pull_content(page_url)
        try:
            location_name = store.find("span", {"itemprop": "name"}).text.strip()
        except:
            location_name = store.title.text.split("-")[0].strip()
        city_content = store.find_all("span", {"itemprop": "addressLocality"})
        if not city_content:
            continue
        if len(city_content) > 1:
            street_address = (
                store.find("span", {"itemprop": "streetAddress"}).text.strip()
                + " "
                + city_content[0].text.strip()
            ).rstrip(",")
            city = city_content[1].text.strip().rstrip(",")
        else:
            street_address = (
                store.find("span", {"itemprop": "streetAddress"})
                .text.strip()
                .rstrip(",")
            )
            city = city_content[0].text.strip().rstrip(",")
        state = MISSING
        zip_postal = (
            store.find("span", {"itemprop": "postalCode"}).text.replace(".", "").strip()
        )
        phone = store.find("span", {"itemprop": "telephone"}).text.strip()
        country_code = "GB"
        store_number = MISSING
        location_type = MISSING
        try:
            hours_of_operation = (
                store.find("table", id="opening-times-table")
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
                .replace(",-,", "-")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        try:
            latlong = store.find(
                "script", string=re.compile(r"function loadHandler\(\).*")
            ).string
            latitude = (
                latlong.split('"_readModeLat":')[1].split(',"_readModeLon"')[0].strip()
            )
            longitude = (
                latlong.split('"_readModeLon":')[1]
                .split(',"_readModeMapZoomLevel')[0]
                .strip()
            )
        except:
            latitude = MISSING
            longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
