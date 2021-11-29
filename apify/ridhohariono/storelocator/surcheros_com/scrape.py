from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa
import json

DOMAIN = "surcheros.com"
LOCATION_URL = "https://www.surcheros.com/locations/"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = json.loads(soup.find("script", {"type": "application/ld+json"}).string)
    for row in data["subOrganization"]:
        if "COMING" in row["description"]:
            continue
        page_url = row["url"]
        info = pull_content(page_url)
        location_name = row["name"]
        street_address = row["address"]["streetAddress"].replace(
            ", Donaldson Dining Hall", ""
        )
        city = row["address"]["addressLocality"]
        state = row["address"]["addressRegion"]
        zip_postal = row["address"]["postalCode"]
        country_code = "US"
        phone = MISSING if not row["telephone"] else row["telephone"]
        store_number = MISSING
        location_type = row["@type"]
        latlong = info.find("div", {"class": "gmaps"})
        latitude = latlong["data-gmaps-lat"]
        longitude = latlong["data-gmaps-lng"]
        hoo_content = info.find("section", id="intro").find(
            "div", {"class": "col-md-6"}
        )
        if not hoo_content:
            hoo_content = info.find("section", id="intro")
        hoo_content.find("h2").decompose()
        hoo_content.find("p").decompose()
        try:
            hoo_content.find("a", {"class": "btn btn-brand"}).parent.decompose()
        except:
            pass
        hours_of_operation = (
            hoo_content.get_text(strip=True, separator="@")
            .replace("day@", "day: ")
            .replace("@", ",")
            .replace(",,", ",")
            .strip()
        )
        if "OPENING DECEMBER" in hours_of_operation:
            location_type = "COMING_SOON"
            hours_of_operation = "COMING_SOON"
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
