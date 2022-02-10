from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa


DOMAIN = "laclinica.org"
API_URL = "https://laclinica.org/wp-admin/admin-ajax.php?action=mapp_query&filters=&list=true&query%5Bpost_type%5D=location&url%5Bhref%5D=https%3A%2F%2Flaclinica.org%2Flocations%2F&url%5Bsearch%5D=&debug="
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["data"]["pois"]:
        page_url = row["url"]
        store = pull_content(page_url)
        location_name = row["title"].replace("<br>", " ").strip()
        raw_address = bs(row["body"], "lxml").find("p").text.strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        try:
            phone = (
                store.find("p", {"class": "phone"}).text.replace("Phone:", "").strip()
            )
        except:
            phone = (
                store.find("span", text="Phone:")
                .parent.text.replace("Phone:", "")
                .strip()
            )
        country_code = "US"
        try:
            hours_of_operation = (
                store.find("p", {"class": "hours"}).text.replace("Hours:", "").strip()
            )
        except:
            hours_of_operation = (
                store.find("p", {"class": "dept-hour"})
                .text.replace("Hours:", "")
                .strip()
            )
        location_type = MISSING
        store_number = MISSING
        latitude = row["point"]["lat"]
        longitude = row["point"]["lng"]
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
