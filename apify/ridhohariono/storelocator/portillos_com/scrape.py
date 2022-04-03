from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re
import json

DOMAIN = "portillos.com"
BASE_URL = "https://www.portillos.com"
LOCATION_URL = "https://www.portillos.com/locations/"
API_LOCATION = "https://www.portillos.com/ajax/location/getAllLocations/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}

HEADERS_API = {
    "content-Type": "application/json;charset=UTF-8",
    "s": "mjA1AiWID8JqImr3iMoEXFUpeuasRBIglY+FBqETplI=",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find("div", {"class": "table-hours"})
    hoo = hoo_content.get_text(strip=True, separator=",").replace("day,", "day: ")
    tomorrow = (
        hoo_content.find("div", {"class": "tr-hours"})
        .find("div", {"class": "td-hours-right"})
        .find("span")["data-yext-field"]
        .replace("hours-", "")
    ).title()
    hoo = hoo.replace("Tomorrow,", tomorrow + ": ")
    return hoo


def fetch_data():
    log.info("Fetching store_locator data")
    payload = json.dumps({"locations": [], "all": "y"})
    data = session.post(API_LOCATION, headers=HEADERS_API, data=payload).json()
    for row in data["locations"]:
        page_url = BASE_URL + row["Url"]
        location_name = row["Name"]
        if not row["Address"]:
            (
                street_address,
                city,
                state,
                zip_postal,
            ) = getAddress(f"{row['City']}, {row['State'], row['Zip']}")
        else:
            street_address = row["Address"]
            city = row["City"]
            state = row["State"]
            zip_postal = row["Zip"]
        phone = row["Phone"]
        country_code = "US"
        store_number = row["Id"]
        hours_of_operation = get_hoo(page_url)
        latitude = row["Lat"]
        longitude = row["Lng"]
        if "Opening Soon" in row["HoursMessage"]:
            location_type = "COMING_SOON"
        else:
            location_type = "OPEN"
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
