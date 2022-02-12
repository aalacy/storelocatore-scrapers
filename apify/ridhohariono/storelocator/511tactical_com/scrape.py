from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "511tactical.com"
BASE_URL = "https://www.511tactical.com/"
LOCATION_URL = "https://www.511tactical.com/store-locator"
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
            country = data.country
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country is None or len(country) == 0:
                country = MISSING
            return street_address, city, state, zip_postal, country
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.location-row.row div.info-location.col-sm-6.col-lg-4")
    for row in contents:
        link = row.find("a")
        if not link:
            continue
        if DOMAIN in link["href"]:
            page_url = link["href"]
        else:
            page_url = (BASE_URL + link["href"]).replace(".com//", ".com/")
        store = pull_content(page_url)
        location_name = (
            store.find("div", id="location-title").text.replace("–", "-").strip()
        )
        raw_address = " ".join(
            store.find("h3", text="Address")
            .find_next("div", {"class": "location-details-content"})
            .get_text(strip=True, separator=",")
            .replace("\n", "")
            .split()
        ).strip()
        street_address, city, state, zip_postal, country = getAddress(raw_address)
        phone = (
            store.find("h3", text="Phone")
            .find_next("div", {"class": "location-details-content"})
            .text.strip()
        )
        hours_of_operation = (
            store.find("h3", text="Hours of Operation")
            .find_next("div", {"class": "location-details-content"})
            .get_text(strip=True, separator=" ")
        )
        country_code = "US" if country == MISSING else country
        store_number = MISSING
        location_type = MISSING
        latlong = (
            store.find("h3", text="GEO")
            .find_next("div", {"class": "location-details-content"})
            .text.strip()
            .replace(" ", "")
            .split(",")
        )
        latitude = latlong[0]
        longitude = latlong[1]
        log.info(
            "Append {}: {} => {}".format(country_code, location_name, street_address)
        )
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
