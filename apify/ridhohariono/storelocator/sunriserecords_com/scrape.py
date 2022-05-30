import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "sunriserecords.com"
BASE_URL = "https://www.sunriserecords.com/"
LOCATION_URL = "https://www.sunriserecords.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


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
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return MISSING, MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.locations-cont tr")
    for row in contents:
        info = row.get_text(strip=True, separator="@@").split("@@")
        if len(info) < 4:
            continue
        location_name = info[0].strip()
        if len(info) > 5:
            raw_address = ", ".join(info[1:-3]).replace("Award Winning!,", "").strip()
            phone = "".join(info[3:-1]).strip()
        else:
            raw_address = ", ".join(info[1:-2]).replace("Award Winning!,", "").strip()
            phone = info[-2].strip()
        street_address, city, _, zip_postal = getAddress(raw_address)
        if city == MISSING or city == "Red":
            addr_split = raw_address.split(",")
            if len(addr_split) > 2:
                city = addr_split[-1]
        city = city.replace("International Airport", "").replace("44", "").strip()
        if zip_postal == MISSING:
            zip_postal = raw_address.split(",")[-2].strip()
            if len(zip_postal) > 8:
                zip_postal = MISSING
        if len(zip_postal) == 3:
            zip_postal = info[1].split(",")[1].strip()
        state = row.parent.parent.parent.find_previous("h2").text.strip()
        country_code = "CA"
        phone = phone.replace("Belleville", "").strip()
        hours_of_operation = MISSING
        location_type = MISSING
        store_number = MISSING
        map_link = row.find("a", text="DIRECTIONS")["href"]
        latitude, longitude = get_latlong(map_link)
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
