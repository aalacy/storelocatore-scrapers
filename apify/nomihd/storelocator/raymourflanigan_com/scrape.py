# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

website = "raymourflanigan.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}

url_list = []


def fetch_records_for(zipcode):
    log.info(f"pulling records for zipcode: {zipcode}")
    search_url = (
        "https://www.raymourflanigan.com/api/custom/location-search"
        "?postalCode={}&distance=100&includeShowroom"
        "Locations=true&includeOutletLocations=true&include"
        "ClearanceLocations=true&includeAppointments=true"
    )

    stores_req = session.get(search_url.format(zipcode), headers=headers)
    stores = json.loads(stores_req.text)["locations"]
    yield stores


def process_record(raw_results_from_one_zipcode):
    for stores in raw_results_from_one_zipcode:
        for store_json in stores:
            if store_json["url"] not in url_list:
                url_list.append(store_json["url"])

                page_url = "https://www.raymourflanigan.com" + store_json["url"]
                log.info(page_url)
                locator_domain = website
                location_name = store_json["displayName"]
                street_address = store_json["addressLine1"]
                city = store_json["city"]
                state = store_json["stateProvince"]
                zip = store_json["postalCode"]
                country_code = "US"

                store_number = store_json["businessUnitCode"]
                phone = store_json["phoneNumber"]

                location_type = "Showroom"
                if store_json["clearanceCenter"] is True:
                    location_type = "clearanceCenter"
                if store_json["outlet"] is True:
                    location_type = "outlet"

                hours_of_operation = ""
                hours = store_json["hours"]
                hours_list = []
                for key, hour in hours.items():
                    if (
                        hours[key] is not None
                        and hours[key]["open"] is not None
                        and hours[key]["close"] is not None
                    ):
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

                latitude = store_json["latitude"]
                longitude = store_json["longitude"]

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
    with SgWriter() as writer:
        results = parallelize(
            search_space=static_zipcode_list(
                radius=10, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=32,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
