from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re
from urllib.parse import unquote


DOMAIN = "deltasoniccarwash.com"
BASE_URL = "https://deltasoniccarwash.com/"
LOCATION_URL = "https://deltasoniccarwash.com/locations.html"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()
MISSING = SgRecord.MISSING


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
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


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    contents = soup.find_all("div", {"class": "location-links1"})
    for content in contents:
        urls = content.find_all("a", {"data-href": re.compile(r"page:.*")})
        for url in urls:
            if len(url.text) > 0:
                store_dict = {"link": BASE_URL + url["href"], "address": url.text}
                store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    sotre_info = fetch_store_urls()
    for row in sotre_info:
        page_url = row["link"]
        soup = pull_content(page_url)
        content = soup.find(
            "div", {"class": "location-links1", "data-muse-type": "txt_frame"}
        )
        parent = content.find("h1", {"class": "Location-H1-Heading"})
        location_name = parent.text
        map_link = soup.find("iframe", {"class": "actAsDiv"})["src"]
        raw_address = unquote(map_link.split("&q=")[1].split("&aq=")[0])
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = MISSING
        get_hoo = content.find("h3", text="Car Wash")
        if not get_hoo:
            get_hoo = content.find("h3", {"class": "Location-Heading2020"})
        hours_of_operation = (
            get_hoo.find_next("p")
            .get_text(strip=True, separator=",")
            .replace("Pre-Sale Hours:,", "")
        )
        phone = (
            content.find("a", {"href": re.compile(r"tel:.*")})["href"]
            .replace("tel:", "")
            .strip()
        )
        if "Coming soon" in hours_of_operation:
            location_type = "COMING_SOON"
        else:
            location_type = "OPEN"
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
