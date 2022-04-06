from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re
import json

DOMAIN = "scottybrownsrestaurant.com"
BASE_URL = "https://www.scottybrownsrestaurant.com"
LOCATION_URL = "https://www.scottybrownsrestaurant.com/"
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
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = (
        soup.find("nav", {"id": "mainNavigation"})
        .find("div", {"class": "folder"})
        .find("div", {"class": "subnav"})
    )
    store_info = content.find_all("a")
    for row in store_info:
        page_url = BASE_URL + row["href"]
        content = pull_content(page_url)
        location_name = content.find("h1", {"class": "page-title"}).text.strip()
        info = content.find("div", {"class": "sqs-block map-block sqs-block-map"})
        info_json = json.loads(info["data-block-json"])["location"]
        raw_address = f"{info_json['addressLine1']}, {info_json['addressLine2']}"
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone_pattern = r"(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}"
        phone = re.search(
            phone_pattern,
            content.find(
                "p",
                style="white-space:pre-wrap;",
                text=re.compile(r".*give us a call at.*"),
            ).text,
        ).group()
        hoo = content.find("h3", text="HOURS OF OPERATION").parent
        hours_of_operation = (
            hoo.get_text(strip=True, separator=",")
            .replace(
                "We are serving brunch on Saturdays & Sundays from 10am - 2pm!", ""
            )
            .replace("Flexible daily based on flight schedules", "")
            .replace("HOURS OF OPERATION", "")
            .lstrip(",")
        ).strip()
        store_number = MISSING
        country_code = "US"
        if "TEMPORARILY CLOSED" in hours_of_operation:
            location_type = "TEMPORARILY CLOSED"
        else:
            location_type = "OPEN"
        latitude = info_json["mapLat"]
        longitude = info_json["mapLng"]
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
