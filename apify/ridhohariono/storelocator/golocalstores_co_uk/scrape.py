from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re


DOMAIN = "golocalstores.co.uk"
LOCATION_URL = "https://golocalstores.co.uk/store-finder"
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
    contents = soup.find(
        "section", {"class": "grid-container grid-parent clearfix"}
    ).find_all("script", string=re.compile(r"new google\.maps\.InfoWindow.*"))
    for row in contents:
        store = bs(
            re.search(
                r"new google\.maps\.InfoWindow\({content:\s+\'(.*)'}\);", row.string
            ).group(1),
            "lxml",
        )
        page_url = store.find("a")["href"].replace("/\\", "/").replace("\\", "/")
        info = store.get_text(strip=True, separator="@@").split("@@")
        location_name = info[0]
        raw_address = ",".join(info[1:])
        street_address, city, state, zip_postal = getAddress(raw_address)
        addr_split = raw_address.split(",")
        if len(addr_split[-1]) < 5:
            zip_postal = " ".join(addr_split[-2:]).strip()
        else:
            zip_postal = addr_split[-1].strip()
        if city == MISSING:
            if len(addr_split[-1]) < 5:
                city = addr_split[-3].strip()
            else:
                city = addr_split[-2].strip()
        if zip_postal == MISSING:
            if len(addr_split[-1]) < 5:
                zip_postal = " ".join(addr_split[-2:]).strip()
            else:
                zip_postal = addr_split[-1].strip()
        phone = MISSING
        country_code = "GB"
        hours_of_operation = MISSING
        location_type = MISSING
        store_number = MISSING
        try:
            latlong = (
                row.text.strip()
                .split("google.maps.LatLng(")[1]
                .split(")")[0]
                .split(",")
            )
            latitude = latlong[0]
            longitude = latlong[1]
        except:
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
