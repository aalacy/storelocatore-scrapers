from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


DOMAIN = "citgo.com"
API_URL = "https://www.citgo.com/api/locations/search?location={}"
LOCATION_URL = "https://www.citgo.com/station-locator"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def build_hours(row):
    hours = ""
    if "hrsmonstart" in row and row["hrsmonstart"]:
        hours = hours + " mon " + row["hrsmonstart"] + " - " + row["hrsmonend"]
    if "hrstuesstart" in row and row["hrstuesstart"]:
        hours = hours + " tues " + row["hrstuesstart"] + " - " + row["hrstuesend"]
    if "hrswedstart" in row and row["hrswedstart"]:
        hours = hours + " wed " + row["hrswedstart"] + " - " + row["hrswedend"]
    if "hrsthursstart" in row and row["hrsthursstart"]:
        hours = hours + " thurs " + row["hrsthursstart"] + " - " + row["hrsthursend"]
    if "hrsfristart" in row and row["hrsfristart"]:
        hours = hours + " fri " + row["hrsfristart"] + " - " + row["hrsfriend"]
    if "hrssatstart" in row and row["hrssatstart"]:
        hours = hours + " sat " + row["hrssatstart"] + " - " + row["hrssatend"]
    if "hrssunstart" in row and row["hrssunstart"]:
        hours = hours + " sun " + row["hrssunstart"] + " - " + row["hrssunend"]
    return hours.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=10,
        max_search_results=5,
    )
    for zipcode in search:
        url = API_URL.format(zipcode)
        log.info("Pull content => " + url)
        try:
            stores = session.get(url, headers=HEADERS).json()
        except:
            continue
        for row in stores["locations"]:
            location_name = row["name"]
            street_address = row["address"]
            city = row["city"]
            state = row["state"]
            zip_postal = row["zip"]
            country_code = row["country"]
            phone = row["phone"]
            hours_of_operation = build_hours(row)
            location_type = MISSING
            store_number = row["number"]
            latitude = row["latitude"]
            longitude = row["longitude"]
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
