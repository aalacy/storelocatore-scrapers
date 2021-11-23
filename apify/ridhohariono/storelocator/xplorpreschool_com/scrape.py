from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "xplorpreschool.com"
BASE_URL = "https://www.xplorpreschool.com"
API_URL = "https://www.xplorpreschool.com/wp-admin/admin-ajax.php?action=nobel_schools&change=true&radius=10000&program=All&type=latlng&location%5Blat%5D=36.02048110961914&location%5Blng%5D=-115.28479766845703"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


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


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find(
        re.compile(r"li|div"), {"class": re.compile(r"detail hours.*")}
    )
    if hoo_content:
        hoo = (
            hoo_content.get_text(strip=True, separator=",")
            .replace("Hours,", "")
            .replace("Academic:", "")
        )
        hoo = re.sub(r"Grades.*", "", hoo).rstrip(",").strip()
        hoo = re.sub(r"Extended:.*", "", hoo).rstrip(",").strip()
    else:
        hoo = MISSING
    return hoo


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()["data"]
    for row in data:
        if "BASIS Independent" in row["name"]:
            page_url = row["contact"].lower()
        else:
            page_url = row["url"].lower()
        location_name = row["name"]
        street_address = re.sub(r"\(.*\)", "", row["address"]).strip()
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        phone = row["phone"]
        location_type = re.search(
            r"^(?:https?:\/\/)?(?:[^@\n]+@)?(?:[^.]+\.)?([^:\/\n\?\=]+)\.", page_url
        ).group(1)
        if "xplorpreschool" in page_url:
            hours_of_operation = get_hoo(page_url)
        else:
            hours_of_operation = MISSING
        country_code = "US"
        store_number = MISSING
        latitude = row["lat"]
        longitude = row["lng"]
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
            raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.RAW_ADDRESS,
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
