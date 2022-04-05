from sglogging import sglog
from sgrequests import SgRequests, SgRequestError
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="thelittleclinic.com")


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
        max_search_distance_miles=200,
    )
    for i, zip_code in enumerate(zip_codes):

        log.info(
            "Searching: %s | Items remaining: %s"
            % (zip_code, zip_codes.items_remaining())
        )

        link = (
            "https://www.thelittleclinic.com/appointment-management/v1/clinics?filter.businessName=tlc&filter.freeFormAddress=%s&filter.maxResults=100&page.size=500"
            % zip_code
        )
        r = session.get(
            link,
            headers=headers,
        )
        if isinstance(r, SgRequestError):
            continue
        json_data = r.json()
        j = json_data["data"]["clinics"]

        for i in j:
            locator_domain = "https://www.thelittleclinic.com/"
            location_name = i["name"]
            street_address = " ".join(i["address"]["addressLines"])
            log.info(location_name)
            city = i["address"]["cityTown"]
            state = i["address"]["stateProvince"]
            zip = i["address"]["postalCode"]
            country_code = "US"
            store_number = i["id"]
            try:
                phone = i["phone"]
            except:
                phone = "<MISSING>"
            if i["isSchedulerEnabled"]:
                location_type = "Scheduling Appointments Available"
            else:
                location_type = "Scheduling Appointments Currently Unavailable"

            latitude = i["location"]["lat"]
            longitude = i["location"]["lng"]
            zip_codes.found_location_at(latitude, longitude)
            hours_of_operation = "<INACCESSIBLE>"

            id_num = str(i["id"])
            page_url = "https://www.thelittleclinic.com/clinic-details/%s/%s" % (
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
