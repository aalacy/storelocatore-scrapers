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

DOMAIN = "micasitarestaurants.com"
BASE_URL = "https://www.micasitarestaurants.com"
LOCATION_URL = "https://www.micasitarestaurants.com/locations/"
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
    content = json.loads(soup.find("script", {"type": "application/ld+json"}).string)
    for row in content["subOrganization"]:
        page_url = row["hasMap"]
        info = pull_content(page_url)
        location_name = row["name"]
        street_address = row["address"]["streetAddress"]
        city = row["address"]["addressLocality"]
        state = row["address"]["addressRegion"]
        zip_postal = row["address"]["postalCode"]
        phone = row["telephone"]
        hoo_content = info.find("section", {"id": "intro"}).find_all("p")
        hours_of_operation = ""
        for hoo in hoo_content:
            if hoo.find("a"):
                continue
            hours_of_operation += hoo.text.strip() + ", "
        if "day," in hours_of_operation:
            hours_of_operation = hours_of_operation.replace("day,", "day:")
        else:
            hours_of_operation = re.sub(r"(day)\d", r"\1:", hours_of_operation)
        hours_of_operation = re.sub(
            r",$", "", hours_of_operation.replace(", ,", "").strip()
        )
        location_type = row["@type"]
        country_code = "US"
        store_number = MISSING
        latlong = info.find("div", {"class": "gmaps"})
        latitude = latlong["data-gmaps-lat"]
        longitude = latlong["data-gmaps-lng"]
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
                    SgRecord.Headers.PAGE_URL,
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
