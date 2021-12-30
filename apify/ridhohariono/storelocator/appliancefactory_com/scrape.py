import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import json

DOMAIN = "appliancefactory.com"
BASE_URL = "https://appliancefactory.com"
LOCATION_URL = "https://www.appliancefactory.com/store_finder.html"
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
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_json(soup):
    element = soup.find("script", string=re.compile(r"var\s+locations\s+=\s+"))
    content = re.search(r"var\s+locations\s+=\s+\[\n+(.*)", element.string)
    data = json.loads(f'[{re.sub(r",$", "", content.group(1))}]')
    return data


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = get_json(soup)
    for row in data:
        page_url = BASE_URL + row["url"]
        if "indianaonline" in page_url or "columbusonline" in page_url:
            continue
        content = pull_content(page_url)
        location_name = row["store_name"]
        street_address = row["address"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        store_number = MISSING
        phone = (
            content.find("div", {"id": "location-phone-section"})
            .text.replace("Phone", "")
            .replace("Online Sales", "")
            .replace("\n", "")
            .strip()
        )
        country_code = "US"
        location_type = "appliancefactory"
        latitude = row["latitude"]
        longitude = row["longitude"]
        try:
            hoo_content = content.find("div", {"id": "location-hours-section"}).find(
                "table"
            )
        except:
            hoo_content = content.find("div", {"class": "location-hours"})
        hours_of_operation = (
            hoo_content.get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace("Today's Hours:", "")
            .strip()
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
