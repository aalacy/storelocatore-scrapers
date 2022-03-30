import json
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "pjscoffee.com"
BASE_URL = "https://locations.pjscoffee.com"
LOCATION_URL = "https://locations.pjscoffee.com/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def parse_hours(table):
    if not table:
        return "<MISSING>"
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(BASE_URL)
    state_links = soup.select("ul.browse-list li a")
    for state_link in state_links:
        state_page = pull_content(state_link["href"])
        city_links = state_page.select("ul.map-list a")
        for city_link in city_links:
            city_page = pull_content(city_link["href"])
            stores_link = city_page.select(
                "ul.map-list div.map-list-item-header-right a"
            )
            for link in stores_link:
                store_urls.append(link["href"])
    log.info("Found {} Stores ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    for page_url in page_urls:
        soup = pull_content(page_url)
        info = json.loads(soup.find("script", type="application/ld+json").string)[0]
        location_name = info["name"]
        addr = info["address"]
        street_address = addr["streetAddress"]
        city = addr["addressLocality"]
        state = addr["addressRegion"]
        zip_postal = addr["postalCode"]
        country_code = "US"
        phone = addr["telephone"]
        hours_of_operation = info["openingHours"].strip()
        store_number = MISSING
        location_type = MISSING
        try:
            coming_soon = soup.find("div", {"class": "hours-status"}).text.strip()
            if "Coming Soon" in coming_soon:
                location_type = "COMING SOON"
        except:
            pass
        latitude = info["geo"]["latitude"]
        longitude = info["geo"]["longitude"]
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
