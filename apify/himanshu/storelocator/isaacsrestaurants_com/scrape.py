from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "isaacsrestaurants.com"
BASE_URL = "https://www.isaacsrestaurants.com"
LOCATION_URL = "https://www.isaacsrestaurants.com/locations/"
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


def get_latlong(url):
    latlong = re.search(r"(-?[\d]*\.[\d]*),(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_info = soup.find("section", {"class": "locations_list"}).find_all(
        "a", text="Click for Details"
    )
    for row in store_info:
        page_url = row["href"]
        content = pull_content(page_url)
        info = content.find("section", {"class": "location_info"})
        location_name = content.find("h1", {"class": "entry-title"}).text.strip()
        raw_address = re.sub(
            r"This location only.*",
            "",
            info.find("address")
            .get_text(strip=True, separator=",")
            .replace("The Shops of Traintown", ""),
        )
        raw_address = re.sub(r"\(.*GPS\)", "", raw_address).replace("Route", "")
        street_address, city, state, zip_postal = getAddress(raw_address)
        if "741 East" in street_address:
            street_address = "226 Gap Road"
        phone = (
            info.find("div", {"class": "phones"})
            .find("div")
            .text.replace("Phone:", "")
            .strip()
        )
        hours_of_operation = re.sub(
            r",Isaac’s.*",
            "",
            info.find("div", {"class": "hours"})
            .get_text(strip=True, separator=",")
            .replace("Hours of Operation:,", "")
            .replace(
                "South York Isaac’s is open once more with new temporary hours:", ""
            )
            .replace("These hours are only at South York Isaac’s location.", "")
            .replace(",CLOSED", ": CLOSED")
            .lstrip(","),
        ).lstrip(",")
        if not re.search(r".*am|.*pm|.*CLOSED", hours_of_operation, re.IGNORECASE):
            hours_of_operation = MISSING
        store_number = MISSING
        country_code = "US"
        location_type = "isaacsrestaurants"
        maps_link = content.find("a", {"href": re.compile(r".*\/maps\/dir\/.*")})[
            "href"
        ]
        latitude, longitude = get_latlong(maps_link)
        log.info(
            "Append {} => {} ({}, {})".format(
                location_name, street_address, latitude, longitude
            )
        )
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
