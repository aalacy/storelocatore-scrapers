from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
website = "servicemasterrestore_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://www.servicemasterrestore.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        zips = DynamicZipSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
        )
        for zip_code in zips:
            log.info(f"{zip_code} | remaining: {zips.items_remaining()}")
            url = (
                "https://www.servicemasterrestore.com/locations/?CallAjax=GetLocations"
            )
            payload = (
                '{"zipcode":"' + zip_code + '","distance":"250","tab":"ZipSearch"}'
            )
            loclist = session.post(url, headers=headers, data=payload).json()
            if not loclist:
                continue
            for loc in loclist:
                try:
                    location_name = loc["FranchiseLocationName"]
                except:
                    continue
                page_url = "https://www.servicemasterrestore.com" + loc["Path"]
                store_number = loc["FranchiseLocationID"]
                log.info(location_name)
                phone = loc["Phone"]
                latitude = loc["Latitude"]
                longitude = loc["Longitude"]
                try:
                    street_address = loc["Address1"] + " " + loc["Address2"]
                except:
                    street_address = loc["Address1"]
                city = loc["City"]
                state = loc["State"]
                country_code = loc["Country"]
                zip_postal = loc["ZipCode"]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=MISSING,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=150,
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
