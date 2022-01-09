# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgscrape.simple_utils import parallelize
from sgzip.dynamic import DynamicGeoSearch
from sgpostal import sgpostal as parser

website = "pizzahut.com.sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "apiapse1.phdvasia.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/plain, */*",
    "lang": "en",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "client": "0dbf8474-326c-4bde-b021-ec9f535dd5e8",
    "origin": "https://www.pizzahut.com.sg",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.pizzahut.com.sg/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_records_for(coords):
    lat = coords[0]
    lng = coords[1]
    log.info(f"pulling records for coordinates: {lat,lng}")
    # Your scraper here

    search_url = "https://apiapse1.phdvasia.com/v1/product-hut-fe/localizations"
    params = (
        ("location", f"{lng},{lat}"),
        ("limit", "1000"),
        ("openingHour", "1"),
    )

    stores_req = session.get(search_url, headers=headers, params=params)
    stores = []

    try:
        stores = json.loads(stores_req.text)["data"]["items"]
    except:
        pass

    return stores


def process_record(raw_results_from_one_coordinate):
    stores = raw_results_from_one_coordinate
    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["name"]
        log.info(location_name)
        raw_address = store["address"]
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = store.get("zip_code", "<MISSING>")

        country_code = "SG"
        store_number = store["code"]
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        try:
            hours_of_operation = (
                store["opening_hours"][0]["opening"]
                + " - "
                + store["opening_hours"][0]["closing"]
            )
        except:
            pass
        latitude = store["lat"]
        longitude = store["long"]

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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        search = DynamicGeoSearch(country_codes=["SG"])
        results = parallelize(
            search_space=[(coord) for coord in search],
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
        )
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
