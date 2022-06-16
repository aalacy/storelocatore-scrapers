from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import re


DOMAIN = "sandyspringbank.com"
LOCATION_URL = "https://www.sandyspringbank.com/locations"
API_URL = "https://sandyspringbankv2.locatorsearch.com/GetItems.aspx"
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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=15,
    )
    for lat, lng in search:
        payload = {
            "lat": "39.2369558",
            "lng": "-76.79135579999999",
            "searchby": "FCS|",
            "SearchKey": "",
            "rnd": "1641484157002",
        }
        req = session.post(API_URL, headers=HEADERS, data=payload)
        data = re.sub(r"\<\!\[CDATA\[", " ", req.text)
        data = re.sub(r"\]\]\>", " ", data)
        stores = bs(data, "lxml").find_all("marker")
        log.info(f"Found ({len(stores)}) locations with coord => {lat},{lng}")
        for row in stores:
            location_name = (
                row.find("title")
                .text.replace("Please visit us at our new address.", "")
                .strip()
            )
            street_address = row.find("add1").text.strip()
            ctt = list(row.find("add2").stripped_strings)
            ct = ctt[0].split(",")
            city = ct[0].strip()
            state = ct[1].strip().split(" ")[0].strip()
            zip_postal = ct[1].strip().split(" ")[1].strip()
            phone = ""
            if len(ctt) > 1:
                phone = ctt[-1].strip()
            country_code = "US"
            hoo_content = (
                row.find("label", text=re.compile("Hours"))
                .parent.find("contents")
                .find("table")
            )
            hours_of_operation = re.sub(
                r"Details.*|Drive-Thru:.*",
                "",
                hoo_content.get_text(strip=True, separator=",").replace(
                    "day:,", "day: "
                ),
                flags=re.IGNORECASE,
            ).strip()
            if len(hours_of_operation) < 5:
                hours_of_operation = hoo_content.find_next("div").text.strip()
            store_number = MISSING
            latitude = row["lat"]
            longitude = row["lng"]
            location_type = MISSING
            if "temporarily closed" in location_name:
                location_type = "TEMP_CLOSED"
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
                raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
            )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
