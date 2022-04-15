from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
website = "firestonecompleteautocare_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.firestonecompleteautocare.com"
MISSING = SgRecord.MISSING


def fetch_data():
    max_results = 30
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=max_results,
    )
    log.info("Running sgzip ..")
    for postcode in search:
        base_link = (
            "https://www.firestonecompleteautocare.com/bsro/services/store/location/get-list-by-zip?zipCode=%s"
            % (postcode)
        )
        try:
            stores = session.get(base_link, headers=headers).json()["data"]["stores"]
        except:
            continue
        for store in stores:
            location_name = store["storeName"]
            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip_postal = store["zip"]
            country_code = "US"
            store_number = store["storeNumber"]
            phone = store["phone"]
            hours_of_operation = ""
            raw_hours = store["hours"]
            for row in raw_hours:
                day = row["weekDay"]
                start = row["openTime"]
                close = row["closeTime"]
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + start + "-" + close
                ).strip()

            try:
                if store["temporarilyClosed"] == "Y":
                    hours_of_operation = "Temporarily Closed"
            except:
                pass

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.found_location_at(latitude, longitude)
            page_url = store["localPageURL"]
            log.info(page_url)

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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
