from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import json

DOMAIN = "bayhealth.org"
BASE_URL = "https://www.bayhealth.org"
API_URL = "https://www.bayhealth.org/api/search"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


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


def get_latlong(data):
    for row in data:
        if row["Key"] == "latlong":
            latlong = row["Value"].split(",")
            return latlong[0], latlong[1]
    return MISSING, MISSING


def fetch_data():
    log.info("Fetching store_locator data")
    payload = {
        "Query": "_templatename:Location AND is_crawlable_b:true",
        "Page": 1,
        "NumberOfResults": 200,
        "Sort": "locationname_s asc",
    }
    data = json.loads(session.post(API_URL, headers=HEADERS, data=payload).json())
    for row in data["Results"]:
        page_url = BASE_URL + row["Path"].replace(" ", "%20")
        content = pull_content(page_url)
        location_name = "Bayhealth " + row["Name"]
        raw_address = (
            content.find("p", {"class": "address-text"})
            .get_text(strip=True, separator=",")
            .replace(",Get Directions", "")
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        try:
            phone = content.find(
                "div", {"class": "location-details-phone"}
            ).text.strip()
        except:
            phone = MISSING
        country_code = "US"
        location_type = MISSING
        store_number = MISSING
        hoo_content = content.find("section", id="hours-of-operation")
        if not hoo_content:
            hours_of_operation = MISSING
        else:
            hours_of_operation = (
                hoo_content.get_text(strip=True, separator=",")
                .replace("Hours:", "")
                .strip()
                .lstrip(",")
            )
        latitude, longitude = get_latlong(row["Fields"])
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
