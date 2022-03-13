from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re
import json


DOMAIN = "connor.com.au"
BASE_URL = "https://www.connor.com.au/au"
API_URL = "https://www.connor.com.au/au/stores/index/dataAjax/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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


def get_hoo(hours_content):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hoo = ""
    try:
        hours = re.sub(r"\d{1}\|", "", hours_content).split(",")
        for i in range(len(days)):
            hoo += days[i] + ": " + hours[i] + ", "
        hours_of_operation = hoo.strip().rstrip(",")
    except:
        hours_of_operation = MISSING
    return hours_of_operation.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.post(API_URL, headers=HEADERS).json()
    for row in data:
        page_url = BASE_URL + row["u"]
        store = pull_content(page_url)
        location_name = row["n"].strip()
        try:
            info = json.loads(
                store.find(
                    "div",
                    {
                        "class": "store-locator-content",
                        "data-mage-init": re.compile(r"\{.*"),
                    },
                )["data-mage-init"]
            )["store"]
            raw_address = info["map"]["address"]
            hours_of_operation = get_hoo(info["dates"]["oh"])
        except:
            raw_address = f'{row["a"][0]}, {row["a"][1]}, {row["a"][3]}, {row["a"][2]}'
            hours_of_operation = get_hoo(row["oh"])
        street_address, city, state, zip_postal = getAddress(raw_address)
        if city == MISSING:
            city = row["a"][1]
        if state == MISSING:
            state = row["a"][3]
        if zip_postal == MISSING:
            zip_postal = row["a"][2]
        country_code = "AU"
        phone = row["p"]
        try:
            type = (
                store.find("div", {"class": "categories"})
                .text.replace("\n", ",")
                .strip()
            )
            if "Retail Store" in type:
                location_type = "Retail Store"
            elif "Outlet Store" in type:
                location_type = "Outlet Store"
        except:
            location_type = MISSING
        store_number = row["i"]
        latitude = row["l"]
        longitude = row["g"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
