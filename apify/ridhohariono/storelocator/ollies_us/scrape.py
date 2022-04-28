from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "ollies.us"
BASE_URL = "https://www.ollies.us"
API_URL = "https://www.ollies.us/admin/locations/ajax.aspx?Page=1&PageSize=50000&Longitude=-74.00597&Latitude=40.71427&City=&State=&F=GetNearestLocations&RangeInMiles=5000"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.post(API_URL, headers=HEADERS).json()
    for row in data["Locations"]:
        if "Coming soon" in row["OpenHours"]:
            continue
        page_url = BASE_URL + row["CustomUrl"]
        location_name = row["Name"] if row["Name"] else "Ollie's Bargain"
        if row["Address2"]:
            street_address = (row["Address1"] + " " + row["Address2"]).strip()
        else:
            street_address = row["Address1"]
        city = row["City"]
        state = row["State"]
        zip_postal = row["Zip"]
        phone = row["Phone"].strip()
        store_number = row["StoreCode"]
        country_code = "US"
        hours_of_operation = row["OpenHours"].replace("<br />", ",").rstrip(",").strip()
        latitude = row["Latitude"]
        longitude = row["Longitude"]
        location_type = "OPEN" if row["IsActive"] == 1 else "CLOSED"
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
