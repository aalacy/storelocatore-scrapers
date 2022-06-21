from sglogging import sglog
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_2
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests

from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="thelittleclinic.com")


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    found = ["540FC003", "01800038"]

    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=30,
        max_search_results=100,
        granularity=Grain_2(),
    )
    with SgRequests() as http:
        for zip_code in zip_codes:

            log.info(
                "Searching: %s | Items remaining: %s"
                % (zip_code, zip_codes.items_remaining())
            )
            link = (
                "https://www.kroger.com/appointment-management/v1/clinics?filter.businessName=tlc&filter.freeFormAddress=%s&filter.maxResults=100&page.size=100"
                % zip_code
            )

            json_data = http.get(link, headers=headers).json()
            j = json_data["data"]["clinics"]

            for i in j:
                locator_domain = "https://www.thelittleclinic.com/"
                location_name = "The Little Clinic"
                street_address = " ".join(i["address"]["addressLines"])
                city = i["address"]["cityTown"]
                state = i["address"]["stateProvince"]
                zip = i["address"]["postalCode"]
                country_code = "US"

                latitude = i["location"]["lat"]
                longitude = i["location"]["lng"]
                zip_codes.found_location_at(latitude, longitude)

                store_number = i["id"]
                if store_number in found:
                    continue
                found.append(store_number)
                try:
                    phone = i["phone"]
                except:
                    phone = "<MISSING>"
                location_type = ""
                hours_of_operation = "<INACCESSIBLE>"

                id_num = str(i["id"])
                page_url = (
                    "https://www.kroger.com/health-services/clinic/details/%s/%s"
                    % (
                        id_num[:3],
                        id_num[3:],
                    )
                )

                try:
                    api_link = (
                        "https://www.kroger.com/appointment-management/v1/clinic-details?filter.businessName=tlc&filter.reasonId=29&filter.divisionNumber=%s&filter.storeNumber=%s"
                        % (id_num[:3], id_num[3:])
                    )
                    page_det = http.get(api_link, headers=headers).json()["data"][
                        "clinicDetails"
                    ]
                    hours_of_operation = " ".join(page_det["weekHours"])
                except:
                    pass

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
            if not j:
                zip_codes.found_nothing()


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
