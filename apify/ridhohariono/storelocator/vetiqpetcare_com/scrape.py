from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import (
    DynamicZipSearch,
    SearchableCountries,
)

DOMAIN = "vetiqpetcare.com"
LOCATION_URL = "https://vetiqpetcare.com/find-a-location/"
API_URL = (
    "https://vetiqpetcare.com/wp-json/clinic-locator/v1/search?&search={}&distance=100"
)
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
    )
    for zip in search:
        search_url = API_URL.format(zip)
        log.info("Pull data from => " + search_url)
        data = session.get(search_url, headers=HEADERS).json()
        for row in data["data"]:
            location_name = row["name"]
            street_address = row["street"].strip().rstrip(",")
            city = row["city"]
            state = row["state"]
            zip_postal = row["zip"]
            raw_address = row["full_address"]
            phone = row["store_phone_number"]
            hoo = ""
            if (
                "standard_weekly_schedule" not in row
                or not row["standard_weekly_schedule"]
            ):
                hoo = row["clinics"][0]["display"].split(" ")
                del hoo[1:-4]
                hours_of_operation = " ".join(
                    " ".join(hoo).replace("until", "-").replace("day", "day: ").split()
                )
            else:
                for hday in row["standard_weekly_schedule"]:
                    hours = hday["clinic_start_at"] + " - " + hday["clinic_end_at"]
                    hoo += hday["clinic_day"] + ": " + hours + ","
                hours_of_operation = " ".join(hoo.rstrip(",").split())
            store_number = MISSING
            country_code = "US"
            latitude = row["latLng"][0]
            longitude = row["latLng"][1]
            location_type = row["brand"]["name"]
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
                    SgRecord.Headers.RAW_ADDRESS,
                }
            ),
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
