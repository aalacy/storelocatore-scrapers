from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "mms.com"
BASE_URL = "https://mms.com"
LOCATION_URL = "https://www.mms.com/en-us/experience-mms/mms-world-stores"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find_all("a", {"class": "white-bg-button"})
    other_country = [
        {"country": "GB", "city": "london"},
        {"country": "CN", "city": "shanghai"},
        {"country": "DE", "city": "berlin"},
    ]
    for row in contents:
        page_url = BASE_URL + row["href"]
        content = pull_content(page_url)
        location_name = (
            content.find("div", {"class": "fc-left-container col-xs-12 col-sm-9"})
            .text.replace("\n", " ")
            .strip()
        )
        info = content.find("div", {"class": "hours"})
        raw_address = re.sub(
            r",Located.*",
            "",
            info.find("div", {"class": "left"})
            .get_text(strip=True, separator=",")
            .replace("STORE INFO,", "")
            .replace("Located in", "")
            .replace("Next to the MGM Hotel & Casino", ""),
        )
        phone = re.search(
            r"(\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}|\+\d{1,2}?[\s.-]\d{3,4}?[\s.-]\d{3,4})",
            raw_address,
        )
        if phone:
            phone = phone.group(1)
            raw_address = raw_address.replace(phone, "")
        else:
            phone = MISSING
        street_address, city, state, zip_postal = getAddress(raw_address)
        hours_of_operation = (
            info.find("div", {"class": "right"})
            .get_text(strip=True, separator=",")
            .replace("HOURS,", "")
            .replace(":,", ": ")
        )
        country_code = "US"
        for other in other_country:
            if city.lower() in other["city"]:
                country_code = other["country"]
                break
        store_number = MISSING
        location_type = MISSING
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
