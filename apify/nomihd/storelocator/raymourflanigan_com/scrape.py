# -*- coding: utf-8 -*-
from datetime import datetime as dt
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt

website = "raymourflanigan.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}

url_list = []


def retry_error_callback(retry_state):
    postal = retry_state.args[0]
    log.error(f"Failure to fetch locations for: {postal}")
    return []


@retry(retry_error_callback=retry_error_callback, stop=stop_after_attempt(5))
def fetch_records_for(zipcode):
    log.info(f"pulling records for zipcode: {zipcode}")
    url = "https://www.raymourflanigan.com/api/custom/location-search"
    params = {
        "postalCode": zipcode,
        "distance": 100,
        "includeShowroomLocations": True,
        "includeOutletLocations": True,
        "includeClearanceLocations": True,
        "includeAppointments": True,
    }
    stores = session.get(url, params=params, headers=headers).json()
    return stores["locations"]


def process_record(raw_results_from_one_zipcode):
    for store in raw_results_from_one_zipcode:
        if store["url"] not in url_list:
            url_list.append(store["url"])

            page_url = "https://www.raymourflanigan.com" + store["url"]
            log.info(page_url)
            locator_domain = website
            location_name = store["displayName"]
            street_address = store["addressLine1"]
            if (
                "addressLine2" in store
                and store["addressLine2"] is not None
                and len(store["addressLine2"]) > 0
            ):
                street_address = street_address + ", " + store["addressLine2"]

            city = store["city"]
            state = store["stateProvince"]
            zip = store["postalCode"]
            country_code = "US"

            store_number = store["businessUnitCode"]
            phone = store["phoneNumber"]

            location_type = "Showroom"
            if store["clearanceCenter"] is True:
                location_type = "Clearance Center"
            if store["outlet"] is True:
                location_type = "Outlet"

            location_name = "Raymour & Flanigan " + location_type
            hours_of_operation = ""
            hours = store["hours"]
            hours_list = []
            for key, hour in hours.items():
                if isinstance(hours[key], dict):
                    if hours[key] and hours[key]["open"] and hours[key]["close"]:
                        day = key
                        if day != "today":
                            hours_list.append(
                                day
                                + ":"
                                + hours[key]["open"]
                                + "-"
                                + hours[key]["close"]
                            )
            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        search = DynamicZipSearch(expected_search_radius_miles=20, country_codes=["US"])
        results = parallelize(
            search_space=[(zipcode) for zipcode in search],
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
        )
        for rec in results:
            writer.write_row(rec)
    log.info("Finished")


if __name__ == "__main__":
    start = dt.now()
    scrape()
    log.info(f"duration: {dt.now() - start}")
