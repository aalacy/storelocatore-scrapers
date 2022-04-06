# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.pl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)

AUTH_HEADERS = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept-Language": "undefined",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Brand": "PH",
    "Source": "WEB",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}


def fetch_data():
    # Your scraper here
    data = '{"deviceUuid":"d520c7a8-421b-4563-b955-f5abc56b97ec","deviceUuidSource":"FINGERPRINT","source":"WEB_PH"}'

    auth_req = session.post(
        "https://kfcdostawa.pl/ordering-api/rest/v1/auth/get-token",
        headers=AUTH_HEADERS,
        data=data,
    ).json()

    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "Accept-Language": "en",
        "sec-ch-ua-mobile": "?0",
        "Authorization": "Bearer " + auth_req["token"],
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Brand": "PH",
        "Source": "WEB",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    }

    stores_req = session.get(
        "https://kfcdostawa.pl/ordering-api/rest/v2/restaurants/", headers=headers
    )

    stores = json.loads(stores_req.text)["restaurants"]
    for store in stores:
        log.info(f"pulling info for store ID: {store['id']}")
        store_req = session.get(
            f"https://kfcdostawa.pl/ordering-api/rest/v1/restaurants/{str(store['id'])}/DELIVERY",
            headers=headers,
        )
        try:
            store_json = json.loads(store_req.text)["details"]
        except:
            store_json = store

        locator_domain = website

        location_name = store_json["name"]

        street_address = store_json["addressStreet"]
        if (
            store_json["addressStreetNo"] is not None
            and len(store_json["addressStreetNo"]) > 0
        ):
            street_address = street_address + " " + store_json["addressStreetNo"]

        city = store_json["addressCity"]
        state = "<MISSING>"
        zip = store_json["addressPostalCode"]

        country_code = "PL"

        phone = "<MISSING>"
        try:
            phone = store_json["phoneNo"]
        except:
            pass

        store_number = store_json["id"]

        page_url = "<MISSING>"
        if "storeLocatorUrl" in store_json:
            page_url = f"https://pizzahut.pl/en/restaurants/{str(store_number)}-{store_json['storeLocatorUrl']}"

        location_type = "<MISSING>"

        hours_list = []
        for key in store_json.keys():
            if key == "openMonTo":
                day = "Mon"
                time = store_json["openMonFrom"] + " - " + store_json["openMonTo"]
                hours_list.append(day + ": " + time)
            if key == "openTueTo":
                day = "Tue"
                time = store_json["openTueFrom"] + " - " + store_json["openTueTo"]
                hours_list.append(day + ": " + time)
            if key == "openWedTo":
                day = "Wed"
                time = store_json["openWedFrom"] + " - " + store_json["openWedTo"]
                hours_list.append(day + ": " + time)
            if key == "openThuTo":
                day = "Thu"
                time = store_json["openThuFrom"] + " - " + store_json["openThuTo"]
                hours_list.append(day + ": " + time)
            if key == "openFriTo":
                day = "Fri"
                time = store_json["openFriFrom"] + " - " + store_json["openFriTo"]
                hours_list.append(day + ": " + time)
            if key == "openSatTo":
                day = "Sat"
                time = store_json["openSatFrom"] + " - " + store_json["openSatTo"]
                hours_list.append(day + ": " + time)
            if key == "openSunTo":
                day = "Sun"
                time = store_json["openSunFrom"] + " - " + store_json["openSunTo"]
                hours_list.append(day + ": " + time)

        if len(hours_list) <= 0:
            try:
                hours_list.append(
                    store_json["openHours"][0]["openFrom"]
                    + " - "
                    + store_json["openHours"][0]["openTo"]
                )
            except:
                pass

        hours_of_operation = "; ".join(hours_list).strip()

        try:
            latitude = store_json["lat"]
            longitude = store_json["lng"]
        except:
            latitude = store_json["geoLat"]
            longitude = store_json["geoLng"]
            pass

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
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
