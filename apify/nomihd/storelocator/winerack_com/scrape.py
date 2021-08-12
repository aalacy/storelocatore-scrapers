# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "winerack.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "maps.googleapis.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "*/*",
    "x-client-data": "CLC1yQEIhbbJAQimtskBCMS2yQEIqZ3KAQjN0MoBCKCgywEI3PLLAQjv8ssBCM32ywEItPjLAQie+csBCPT5ywE=",
    "origin": "https://www.winerack.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


id_list = []


def fetch_records_for(zipp):
    log.info(f"pulling records for zipcode: {zipp}")
    params = (
        ("address", zipp),
        ("key", "AIzaSyBBTHyhVqDIYmp8_dyo4ziGrRpR6XcvRtk"),
    )
    search_url = "https://maps.googleapis.com/maps/api/geocode/json"

    stores = []
    stores_req = session.get(search_url, headers=headers, params=params)

    try:
        stores = json.loads(stores_req.text)["results"]
    except:
        pass

    return stores


def process_record(raw_results_from_one_zipcode):
    stores = raw_results_from_one_zipcode
    for store in stores:
        if store["place_id"] in id_list:
            continue

        id_list.append(store["place_id"])
        log.info(store["place_id"])
        store_req = session.get(
            "https://maps.googleapis.com/maps/api/place/details/json?reference={}&&sensor=true&key=AIzaSyBBTHyhVqDIYmp8_dyo4ziGrRpR6XcvRtk".format(
                str(store["place_id"])
            ),
            headers=headers,
        )
        if json.loads(store_req.text)["status"] == "OK":
            store_json = json.loads(store_req.text)["result"]
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store_json["name"]
            raw_address = store_json["formatted_address"]

            street_address = ""
            city = ""
            state = ""
            zip = ""
            country_code = "CA"
            store_number = store["place_id"]
            phone = store.get("formatted_phone_number", "<MISSING>")

            location_type = "<MISSING>"
            hours = store_json.get("opening_hours", None)
            hours_of_operation = "<MISSING>"
            if hours:
                hours = hours.get("weekday_text", [])
                hours_of_operation = "; ".join(hours).strip()

            latitude = store_json["geometry"]["location"]["lat"]
            longitude = store_json["geometry"]["location"]["lng"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        search = DynamicZipSearch(
            expected_search_radius_miles=100, country_codes=["CA"]
        )
        results = parallelize(
            search_space=[(zip_code) for zip_code in search],
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=10,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
