# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

website = "pnc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "apps.pnc.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

id_list = []


def fetch_records_for(coords):
    lat = coords[0]
    lng = coords[1]
    log.info(f"pulling records for coordinates: {lat,lng}")
    search_url = "https://apps.pnc.com/locator-api/locator/api/v2/location/?latitude={}&longitude={}&radius=100&radiusUnits=mi&branchesOpenNow=false"

    stores_req = session.get(search_url.format(lat, lng), headers=headers)
    stores = json.loads(stores_req.text)["locations"]
    yield stores


def process_record(raw_results_from_one_coordinate):
    for stores in raw_results_from_one_coordinate:
        for store in stores:
            if store["locationType"]["locationTypeDesc"] != "ATM":
                continue
            if store["partnerFlag"] == "1":
                continue
            if store["locationId"] in id_list:
                continue

            id_list.append(store["locationId"])

            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["locationName"]
            street_address = store["address"]["address1"]
            if (
                store["address"]["address2"] is not None
                and len(store["address"]["address2"]) > 0
            ):
                street_address = street_address + ", " + store["address"]["address2"]

            city = store["address"]["city"]
            state = store["address"]["state"]
            zip = store["address"]["zip"]
            country_code = "US"

            store_number = store["locationId"]
            phone = "<MISSING>"

            location_type = store["locationType"]["locationTypeDesc"]
            hours_of_operation = "<MISSING>"
            latitude = store["address"]["latitude"]
            longitude = store["address"]["longitude"]

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
    with SgWriter() as writer:
        results = parallelize(
            search_space=static_coordinate_list(
                radius=100, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=32,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")

    log.info("Finished")


if __name__ == "__main__":
    scrape()
