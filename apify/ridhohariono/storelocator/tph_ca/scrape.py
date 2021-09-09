import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "tph.ca"
BASE_URL = "https://tph.ca/"
LOCATION_URL = "https://www.tph.ca/printing-near-me"
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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)!3d([\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def get_json_content(soup):
    try:
        content = soup.find("script", {"type": "application/ld+json"}).string.replace(
            "\n", ""
        )
    except:
        return False
    return json.loads(content)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("div", {"id": "branchSideMenu_list"}).find_all(
        "div", {"class": "branch-list-item__container"}
    )
    for row in contents:
        store_number = re.sub(r"\D+", "", row["onclick"])
        page_url = BASE_URL + store_number
        content = pull_content(page_url)
        info_content = content.find("div", {"id": "branch-infobanner"})
        raw_address = info_content.find("div", {"id": "branch-address"}).get_text(
            strip=True, separator=","
        )
        location_name = "TPH The Printing House"
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = (
            info_content.find("div", {"id": "branch-contact"}).find("p").text.strip()
        )
        country_code = "CA"
        location_type = "The Printing House"
        map_link = content.find("iframe", {"id": "branch-map"})["src"]
        latitude, longitude = get_latlong(map_link)
        hours_of_operation = (
            content.find("div", {"id": "branch-hours"})
            .text.strip()
            .replace("\n", ",")
            .replace("*We run full production until midnight.,", "")
        )
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
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
