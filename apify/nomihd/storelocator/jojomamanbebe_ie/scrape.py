# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.simple_utils import parallelize
from sgzip.dynamic import DynamicGeoSearch

website = "jojomamanbebe.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)

headers = {
    "authority": "www.jojomamanbebe.ie",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.jojomamanbebe.ie/stores",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_records_for(coords):
    lat = coords[0]
    lng = coords[1]
    log.info(f"pulling records for coordinates: {lat},{lng}")
    search_url = "https://www.jojomamanbebe.ie/stores/search/result/"
    params = (
        ("search_string", ""),
        ("latitude", lat),
        ("longitude", lng),
    )

    stores = []
    stores_req = session.get(search_url, headers=headers, params=params)
    try:
        json_str = (
            stores_req.text.split('locationList": ')[1]
            .split('"locationMapName"')[0]
            .strip()
            .strip(", ")
            + "}"
        )

        json_res = json.loads(json_str)

        stores = json_res["locationItems"]
    except:
        pass

    return stores


def process_record(raw_results_from_one_coordinate):
    stores = raw_results_from_one_coordinate
    for no, store in enumerate(stores, 1):

        locator_domain = website

        page_url = (
            "https://www.jojomamanbebe.ie/stores/location/details/id/"
            + store["location_id"]
        )
        log.info(page_url)
        location_name = store["title"].strip()

        location_type = "<MISSING>"

        raw_address = "<MISSING>"

        street_address = store["street"]

        city = store["city"]

        state = store["region"]

        zip = store["zip"]

        country_code = store["country_id"]
        if country_code != "IE":
            continue
        phone = store["phone"]

        hours = json.loads(store["opening_hours"])
        hours_list = []
        for day, tim in hours.items():
            if len(tim["from"]) > 0 and len(tim["to"]) > 0:
                time = tim["from"] + " - " + tim["to"]
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        store_number = store["location_id"]

        latitude, longitude = store["latitude"], store["longitude"]
        if latitude == longitude:
            latitude = longitude = "<MISSING>"

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
        search = DynamicGeoSearch(country_codes=["IE"])
        results = parallelize(
            search_space=[(coords) for coords in search],
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
        )
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
