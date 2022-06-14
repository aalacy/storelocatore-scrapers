from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "footlocker.no"
BASE_URL = "https://stores.footlocker.no/"
LOCATION_URL = "https://stores.footlocker.no/index.html"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_store_urls(url):
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(url)
    content = soup.find("ul", {"class": "c-directory-list-content"})
    state_links = content.find_all("li", {"class": "c-directory-list-content-item"})
    for row in state_links:
        count = row.find("span").text.replace(")", "").replace("(", "")
        if int(count) > 1:
            data = pull_content(BASE_URL + row.find("a")["href"])
            content = data.find("ul", {"class": "c-directory-list-content"})
            location_contents = data.find_all("article", {"class": "LocationCard"})
            for loc in location_contents:
                link = loc.find("a", {"class": "LocationCard-title--link"})
                store_urls.append(BASE_URL + link["href"])
        else:
            link = row.find("a", {"class": "c-directory-list-content-item-link"})
            store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def parse_hours(table):
    if not table:
        return "<MISSING>"
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-location-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-location-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls(LOCATION_URL)
    for page_url in page_urls:
        content = pull_content(page_url)
        address = content.find("address", {"id": "address"})
        location_name = content.find("h1", {"id": "location-name"}).text.strip()
        raw_address = (
            address.get_text(strip=True, separator=",")
            .rstrip(",")
            .replace(",,", ",")
            .strip()
        )
        street_address = address.find("meta", {"itemprop": "streetAddress"})["content"]
        city = address.find("span", {"class": "c-address-city"}).text.strip()
        get_state = address.find(re.compile("span|abbr"), {"class": "c-address-state"})
        if not get_state:
            state = MISSING
        else:
            state = get_state.text.strip()
        zip_postal = address.find(
            "span", {"class": "c-address-postal-code"}
        ).text.strip()
        phone = content.find("span", {"id": "telephone"}).text.strip()
        hours_of_operation = parse_hours(
            content.find("table", {"class": "c-location-hours-details"})
        )
        country_code = address["data-country"]
        location_type = MISSING
        store_number = MISSING
        latitude = content.find("meta", {"itemprop": "latitude"})["content"]
        longitude = content.find("meta", {"itemprop": "longitude"})["content"]
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
            raw_address=raw_address,
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
