import json
import ssl
from bs4 import BeautifulSoup
from sglogging import sglog
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger(logger_name="thelittleclinic.com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
        max_search_distance_miles=500,
        expected_search_radius_miles=500,
    )
    for zip_code in zip_codes:

        log.info(
            "Searching: %s | Items remaining: %s"
            % (zip_code, zip_codes.items_remaining())
        )
        link = (
            "https://www.kroger.com/appointment-management/v1/clinics?filter.businessName=tlc&filter.reasonId=29&filter.freeFormAddress=%s&filter.maxResults=100&page.size=100"
            % zip_code
        )

        driver.get(link)
        soup = BeautifulSoup(driver.page_source, "lxml")
        json_data = json.loads(soup.text)
        j = json_data["data"]["clinics"]

        for i in j:
            locator_domain = "https://www.thelittleclinic.com/"
            location_name = "The Little Clinic"
            street_address = " ".join(i["address"]["addressLines"])
            city = i["address"]["cityTown"]
            state = i["address"]["stateProvince"]
            zip = i["address"]["postalCode"]
            country_code = "US"
            store_number = i["id"]
            if store_number == "540FC003":
                continue
            try:
                phone = i["phone"]
            except:
                phone = "<MISSING>"
            location_type = ""

            latitude = i["location"]["lat"]
            longitude = i["location"]["lng"]
            zip_codes.found_location_at(latitude, longitude)
            hours_of_operation = ""

            id_num = str(i["id"])
            page_url = "https://www.kroger.com/health-services/clinic/details/%s/%s" % (
                id_num[:3],
                id_num[3:],
            )
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

    driver.close()


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
