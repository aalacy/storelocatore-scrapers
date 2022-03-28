# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "identogo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.identogo.com/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Content-Type": "undefined; charset=UTF-8",
}


def fetch_records_for(tup):
    zipcode, session = tup
    log.info(f"pulling records for zipcode: {zipcode}")
    params = (
        ("country", "us"),
        (
            "access_token",
            "pk.eyJ1Ijoia2xlc3VlciIsImEiOiJjaW95cHd0d2UwMXo5dWNtOHNsYXc2ZXFpIn0.yODSFq1nX4hJXw9PWjwVFw",
        ),
        ("types", "region,postcode,place"),
    )

    response = session.get(
        "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json".format(zipcode),
        headers=headers,
        params=params,
    )

    stores = []
    try:
        context = json.loads(response.text)["features"][0]["context"]
        geometry = json.loads(response.text)["features"][0]["geometry"]
        params = (
            ("context", json.dumps(context)),
            ("geometry", json.dumps(geometry)),
            ("placeType", '["postcode"]'),
            ("properties", "{}"),
            ("text", zipcode),
        )
        stores_header = {
            "authority": "www.identogo.com",
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "content-type": "undefined; charset=UTF-8",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.identogo.com/locations",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        }
        search_url = "https://www.identogo.com/ajax/get-locations"
        stores_req = session.get(search_url, headers=stores_header, params=params)
        stores = json.loads(stores_req.text)["success"]["locations"]

    except:
        pass

    return stores


def process_record(raw_results_from_one_zipcode):
    for store in raw_results_from_one_zipcode:

        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["properties"]["info"]["title"]
        street_address = store["properties"]["info"]["address"]

        if (
            store["properties"]["info"]["address2"] is not None
            and len(store["properties"]["info"]["address2"]) > 0
        ):
            street_address = (
                street_address + ", " + store["properties"]["info"]["address2"]
            )

        city = store["properties"]["info"]["city"]
        state = store["properties"]["info"]["state"]
        zip = store["properties"]["info"]["zip"]
        raw_address = street_address + ", " + city + ", " + state + ", " + zip

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        country_code = "US"

        store_number = "<MISSING>"
        phone = "<MISSING>"

        location_type = "<MISSING>"
        if "-" in location_name:
            location_type = location_name.split("-")[1].strip()

        hours_of_operation = store["properties"]["info"]["hours"]
        if "Coming soon" in hours_of_operation:
            continue
        latitude = store["geometry"]["coordinates"][1]
        longitude = store["geometry"]["coordinates"][0]

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
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
            search = DynamicZipSearch(
                country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
            )
            results = parallelize(
                search_space=[(zip, session) for zip in search],
                fetch_results_for_rec=fetch_records_for,
                processing_function=process_record,
            )
            for rec in results:
                writer.write_row(rec)
                count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
