from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl


DOMAIN = "nutrienagsolutions.com"
LOCATION_URL = "https://nutrienagsolutions.com/find-location"
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
    contents = soup.select("ul.locations li")
    for row in contents:
        location_name = row["data-title"].replace('"', "").strip()
        street_address = row["data-address"].replace("\n", ",").replace('"', "").strip()
        city = row["data-city"].replace('"', "").strip()
        state = row["data-state"].replace('"', "").strip()
        try:
            zip_postal = row["data-zipcode"].replace('"', "").strip()
        except:
            zip_postal = MISSING
        try:
            phone_content = row.find("a", {"class": "phone"})
            if phone_content:
                phone = phone_content.text.strip()
            else:
                phone = row["data-phone"].replace('"', "").strip()
        except:
            phone = MISSING
        location_type = row["data-type"].replace('"', "").strip()
        country_code = "US"
        if len(zip_postal.split(" ")) > 1 or "Humboldt" in city:
            country_code = "CA"
        try:
            row.find("a", {"class": "phone"}).decompose()
        except:
            pass
        raw_address = row.find("div", {"class": "address-container"}).get_text(
            strip=True, separator=", "
        )
        if "Divisionoffice" in raw_address:
            location_type = "Divisionoffice"
        elif "Retailbranch" in raw_address:
            location_type = "Retailbranch"
        elif "Storage" in raw_address:
            location_type = "Storage"
        street_address, city, state, zip_postal = getAddress(raw_address)
        street_address = street_address.replace(location_type, "").strip()
        state = state.replace("(Greenfield)", "").strip()
        hours_of_operation = MISSING
        store_number = MISSING
        if location_name == "Moosomin":
            street_address = (
                row["data-address"].replace("\n", ",").replace('"', "").strip()
            )
            city = "Moosomin"
        try:
            latitude = row["data-latitude"]
            longitude = row["data-longitude"]
            if "USA" in [latitude, longitude]:
                country_code = "US"
                latitude = MISSING
                longitude = MISSING
            elif "CAN" in [latitude, longitude]:
                country_code = "CA"
                latitude = MISSING
                longitude = MISSING
            elif "NULL" in [latitude, longitude]:
                latitude = MISSING
                longitude = MISSING
        except:
            latitude = MISSING
            longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
