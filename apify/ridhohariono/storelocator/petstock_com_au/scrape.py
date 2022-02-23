from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import datetime


DOMAIN = "petstock.com.au"
BASE_URL = "https://www.petstock.com.au/pages/store/"
LOCATION_URL = "https://www.petstock.com.au/pages/store-finder"
API_URL = "https://connector.petstock.io/api/location/?services=&distance=10000&postcode=3038&latitude=-41.4592&longitude=147.1808"
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
    data = session.get(API_URL, headers=HEADERS).json()["data"]
    for row in data:
        page_url = BASE_URL + row["name"].lower().replace(" ", "-")
        location_name = row["name"]
        addr = row["address"]
        street_address = f"{addr['address_line1']} {addr['address_line2']}".strip()
        city = addr["suburb"]
        if "2A" in city:
            city = location_name.replace("PETstock", "").strip()
        state = addr["state"]
        zip_postal = addr["postcode"]
        country_code = "AU" if addr["country"] == "Australia" else addr["country"]
        phone = addr["phone"]
        hoo = ""
        for key, val in row["open_hours"].items():
            for day, hour in val.items():
                if day == "Today":
                    day = datetime.datetime.today().strftime("%A")
                if day == "Tomorrow":
                    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
                    day = tomorrow.strftime("%A")
                if not hour["open"]:
                    hours = "Closed"
                else:
                    hours = (
                        hour["open"][:-2]
                        + ":"
                        + hour["open"][2:]
                        + "-"
                        + hour["close"][:-2]
                        + ":"
                        + hour["close"][2:]
                    )
                hoo += day + ": " + hours + ","
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        if "VET" in location_name:
            location_type = "VET"
        store_number = row["id"]
        latitude = row["location"]["lat"]
        longitude = row["location"]["lon"]
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
