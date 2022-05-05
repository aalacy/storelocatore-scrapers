import json
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
website = "thejoint_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.thejoint.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        zips = DynamicZipSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
        )
        for zip_code in zips:
            log.info(f"{zip_code} | remaining: {zips.items_remaining()}")
            search_url = (
                "https://www.thejoint.com/locations?lat=&lng=&search={}"
            ).format(zip_code)
            r = session.get(search_url, headers=headers)
            try:
                loclist = json.loads(
                    r.text.split("TJ.Locations.clinics =")[1].split("}];")[0] + "}]"
                )
            except:
                continue
            for loc in loclist:
                if loc["is_open"] is False:
                    location_type = "COMING SOON"
                else:
                    location_type = MISSING
                page_url = DOMAIN + loc["url_path"]
                log.info(page_url)
                location_name = loc["name"]
                store_number = loc["id"]
                phone = loc["display_phone_1"]
                try:
                    street_address = loc["address_1"] + " " + loc["address_2"]
                except:
                    street_address = loc["address_1"]
                city = loc["city"]
                state = loc["country_state_id"].replace("US-", "")
                zip_postal = loc["zip_code"]
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                country_code = "US"
                hours_of_operation = str(loc["display_all_days_hours"])
                hours_of_operation = (
                    hours_of_operation.replace("': '", " ")
                    .replace("', '", ", ")
                    .replace("'}", "")
                    .replace("{'", "")
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
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
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
