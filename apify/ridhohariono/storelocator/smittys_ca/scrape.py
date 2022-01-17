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

DOMAIN = "smittys.com"
BASE_URL = "https://www.smittys.com"
LOCATION_URL = "https://www.smittys.ca/Select-Location"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find("script", string=re.compile(r"smittys_posts\s+=\s+(.*)"))
    data = json.loads(re.search(r"smittys_posts\s+=\s+(.*)", content.string).group(1))
    for key, val in data.items():
        location_name = val["title"]
        if "Closed" in location_name or "Now Open!" in location_name:
            continue
        raw_address = val["custom_adress"]
        street_address, city, state, zip_postal = getAddress(raw_address)
        store_number = val["id"]
        phone = val["custom_phone"]
        country_code = "CA"
        location_type = "smittys"
        latitude = val["custom_google_lat"]
        longitude = val["custom_google_lng"]
        if (
            not val["custom_restaurant_open_hrs"]
            or len(val["custom_restaurant_open_hrs"]) == 0
        ):
            hours_of_operation = MISSING
        else:
            hoo = (
                bs(val["custom_restaurant_open_hrs"], "lxml")
                .get_text(strip=True, separator=",")
                .replace("Take-out & Delivery Only,", "")
                .split()
            )
            hoo = re.sub(
                r"Buffet.*|Kid.*", "", "".join(hoo), flags=re.IGNORECASE
            ).replace("to", " - ")
            hours_of_operation = ""
            for i in range(len(hoo)):
                if hoo[i].isalpha() and i + 1 < len(hoo) and hoo[i + 1].isnumeric():
                    hours_of_operation += hoo[i] + ": "
                else:
                    hours_of_operation += hoo[i]
            hours_of_operation = hours_of_operation.rstrip(",")
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
                    SgRecord.Headers.STORE_NUMBER,
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
