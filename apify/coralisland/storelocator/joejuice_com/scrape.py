from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from datetime import datetime


DOMAIN = "joejuice.com"
LOCATION_URL = "https://orders.joejuice.com/"
API_URL = "https://joepay-api.joejuice.com/me/stores"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


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


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def fetch_data():
    data = session.get(API_URL, headers=HEADERS).json()
    time_zone_country = {
        "New_York": "US",
        "Los_Angeles": "US",
        "Chicago": "US",
        "London": "UK",
        "Helsinki": "FL",
        "Stockholm": "SW",
        "Copenhagen": "DK",
        "Oslo": "NO",
        "Berlin": "DE",
        "Amsterdam": "NL",
        "Zurich": "Switzerland",
        "Paris": "FR",
        "Vancouver": "CA",
        "Singapore": "SG",
        "Reykjavik": "IS",
        "Brussels": "BE",
        "Shanghai": "CN",
        "Seoul": "KR",
        "Sydney": "AU",
    }
    for store in data:
        time_zone = store["timezone"].split("/")[1]
        if store["timezone"].split("/")[1] in time_zone_country:
            country_code = time_zone_country[time_zone]
        else:
            country_code = MISSING
        location_name = store["name"].strip()
        if store["city"]:
            street_address, _, state, zip_postal = getAddress(store["address"])
            city = store["city"]
        else:
            street_address, city, state, zip_postal = getAddress(store["address"])
        if city == MISSING:
            if "Miami Beach" in location_name:
                city = "Miami"
            if "Aarhus" in location_name:
                city = "Aarhus"
                street_address = street_address.replace(city, "").strip()
        phone = MISSING
        hours_of_operation = []
        raw_hours = store["storeBusinessHours"]
        if raw_hours:
            for row in raw_hours:
                day = (
                    str(row["day"])
                    .replace("0", "Mon")
                    .replace("1", "Tue")
                    .replace("2", "Wed")
                    .replace("3", "Thu")
                    .replace("4", "Fri")
                    .replace("5", "Sat")
                    .replace("6", "Sun")
                )
                if row["closed"]:
                    hour = "closed"
                else:
                    hour = (
                        datetime.strptime(str(row.get("openTime")), "%H%M").strftime(
                            "%I:%M %p"
                        )
                        + "-"
                        + datetime.strptime(str(row.get("closeTime")), "%H%M").strftime(
                            "%I:%M %p"
                        )
                    )
                hours_of_operation.append(day + " " + hour)
        else:
            hours_of_operation = "CLOSED"
        isOpen = store.get("isOpen")
        isOpenTomorrow = store.get("isOpenTomorrow")
        if not isOpen and not isOpenTomorrow:
            hours_of_operation = "CLOSED"
        location_type = MISSING
        store_number = store["externalId"]
        latitude = store["latitude"]
        longitude = store["longitude"]
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
