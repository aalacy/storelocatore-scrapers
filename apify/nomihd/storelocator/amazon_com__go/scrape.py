# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "amazon.com/go"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://hosted.where2getit.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://hosted.where2getit.com/amazon/index.html",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_records_for(zipcode):
    log.info(f"pulling records for zipcode: {zipcode}")
    search_url = "https://hosted.where2getit.com/amazon/rest/locatorsearch?lang=en_US"
    data = {
        "request": {
            "appkey": "2761DE20-B550-11E9-A3F3-055655A65BB0",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "limit": 250,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": zipcode,
                            "country": "US",
                            "latitude": "",
                            "longitude": "",
                        }
                    ]
                },
                "searchradius": "15|25|50|100|250",
                "where": {
                    "status": {"eq": "Launched"},
                    "or": {
                        "hotfoods": {"in": ""},
                        "coffee": {"in": ""},
                        "alcohol": {"in": ""},
                        "returns": {"in": ""},
                        "lockers": {"in": ""},
                    },
                },
                "false": "0",
            },
        }
    }

    stores = []
    stores_req = session.post(search_url, headers=headers, data=json.dumps(data))
    try:
        stores = json.loads(stores_req.text)["response"]["collection"]
    except:
        pass

    return stores


def process_record(raw_results_from_one_coordinate):
    stores = raw_results_from_one_coordinate
    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["name"]
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store.get("city", "<MISSING>")
        state = store.get("state", "<MISSING>")
        zip = store.get("postalcode", "<MISSING>")
        country_code = "US"
        store_number = store["uid"]
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"
        hours_list = []
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        for key in store.keys():
            if key in days:
                day = key
                time = store[day]
                if time is not None:
                    hours_list.append(day + ": " + time)

        if len(hours_list) <= 0:
            try:
                for key in store.keys():
                    if key == "monopen":
                        if store["monopen"]:
                            day = "Monday:"
                            time = store["monopen"] + " - " + store["monclose"]
                            hours_list.append(day + time)
                    if key == "tueopen":
                        if store["tueopen"]:
                            day = "Tuesday:"
                            time = store["tueopen"] + " - " + store["tueclose"]
                            hours_list.append(day + time)
                    if key == "wedopen":
                        if store["wedopen"]:
                            day = "Wednesday:"
                            time = store["wedopen"] + " - " + store["wedclose"]
                            hours_list.append(day + time)
                    if key == "thuopen":
                        if store["thuopen"]:
                            day = "Thursday:"
                            time = store["thuopen"] + " - " + store["thuclose"]
                            hours_list.append(day + time)
                    if key == "friopen":
                        if store["friopen"]:
                            day = "Friday:"
                            time = store["friopen"] + " - " + store["friclose"]
                            hours_list.append(day + time)
                    if key == "satopen":
                        if store["satopen"]:
                            day = "Saturday:"
                            time = store["satopen"] + " - " + store["satclose"]
                            hours_list.append(day + time)
                    if key == "sunopen":
                        if store["sunopen"]:
                            day = "Sunday:"
                            time = store["sunopen"] + " - " + store["sunclose"]
                            hours_list.append(day + time)

            except:
                pass
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
    log.info("Started")
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        search = DynamicZipSearch(
            expected_search_radius_miles=100, country_codes=["US"]
        )
        results = parallelize(
            search_space=[(zipcode) for zipcode in search],
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
        )
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
