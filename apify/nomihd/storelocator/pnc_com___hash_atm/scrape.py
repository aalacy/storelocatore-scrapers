# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
from tenacity import retry, stop_after_attempt
import datetime

website = "pnc.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "apps.pnc.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://apps.pnc.com/locator/search",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

id_list = []


def retry_error_callback(retry_state):
    coord = retry_state.args[0]
    log.error(f"Failure to fetch locations for: {coord}")
    return []


@retry(
    retry_error_callback=retry_error_callback, stop=stop_after_attempt(5), reraise=True
)
def fetch_records_for(coords):
    lat = coords[0]
    lng = coords[1]
    log.info(f"pulling records for coordinates: {lat,lng}")
    search_url = "https://apps.pnc.com/locator-api/locator/api/v2/location/?t={}&latitude={}&longitude={}&radius=100&radiusUnits=mi&branchesOpenNow=false"
    timestamp = str(datetime.datetime.now().timestamp()).split(".")[0].strip()
    stores_req = session.get(
        search_url.format(timestamp, lat, lng), headers=headers, timeout=15
    )
    stores = json.loads(stores_req.text)["locations"]
    return stores


def process_record(raw_results_from_one_coordinate):
    for store in raw_results_from_one_coordinate:
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

        try:
            cInfo = store["contactInfo"]
            if cInfo is not None:
                for contact in cInfo:
                    if "External Phone" in contact["contactType"]:
                        phone = contact["contactInfo"]
                        break
        except:
            pass

        location_type = store["locationType"]["locationTypeDesc"]
        if location_type != "ATM":
            if store["children"] is not None:
                location_type = "BRANCH AND ATM"

        hours_of_operation = "<MISSING>"
        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]

        if location_type == "ATM" or location_type == "BRANCH AND ATM":
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
            max_threads=20,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")

    log.info("Finished")


if __name__ == "__main__":
    scrape()
