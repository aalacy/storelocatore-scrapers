from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
import re
import ast

DOMAIN = "churchspr.com"
LOCATION_URL = "https://www.churchspr.com/restaurantes"
MAP_URL = "https://www-churchspr-com.filesusr.com/html/633736_82c3407e51af445e4061fca174d61d41.html"
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


def get_latlong(map_link):
    if not map_link:
        return MISSING, MISSING
    latlong = re.search(
        r"@(\-?[0-9]+\.[0-9]+),(\-?[0-9]+\.[0-9]+)",
        map_link,
    )
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(MAP_URL)
    script = soup.find("script", string=re.compile(r"var locations.*"))
    data = re.search(r"var locations = (\[.*\]);", script.string, re.DOTALL).group(1)
    stores = ast.literal_eval(data)
    for row in stores:
        content = bs(row[0], "lxml")
        info = content.get_text(strip=True, separator="@").split("@")
        location_name = info[0].strip()
        raw_address = ", ".join(info[1:-2]).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = info[-2].replace("Tel.", "").replace("Tel:", "")
        country_code = "PR"
        location_type = MISSING
        store_number = MISSING
        hours_of_operation = MISSING
        latitude = row[1]
        longitude = row[2]
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
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
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
