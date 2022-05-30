# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bata.com.co"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bata.com.co",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "service-worker-navigation-preload": "true",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    home_req = session.get("https://www.bata.com.co/tiendas", headers=headers)
    json_str = (
        home_req.text.split("__RUNTIME__ = ")[1].strip().split("__STATE__")[0].strip()
    )
    json_runtime = json.loads(json_str)["cacheHints"]
    sha256Hash = ""
    for key in json_runtime.keys():
        if (
            json_runtime[key]["provider"] == "vtex.store-locator@0.x"
            and json_runtime[key]["sender"] == "vtex.store-locator@0.x"
            and json_runtime[key]["version"] == 1
        ):
            sha256Hash = key
            break

    log.info(f"sha256Hash value is: {sha256Hash}")
    search_url = "https://www.bata.com.co/_v/private/graphql/v1"
    params = (
        ("workspace", "master"),
        ("maxAge", "long"),
        ("appsEtag", "remove"),
        ("domain", "store"),
        ("locale", "es-CO"),
    )

    data = {
        "operationName": "getStores",
        "variables": {},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": sha256Hash,
                "sender": "vtex.store-locator@0.x",
                "provider": "vtex.store-locator@0.x",
            },
        },
    }
    stores_req = session.post(search_url, headers=headers, params=params, json=data)
    stores = json.loads(stores_req.text)["data"]["getStores"]["items"]

    for store in stores:
        page_url = "https://www.bata.com.co/store/{}/{}"
        locator_domain = website
        location_name = store["name"]
        street_address = store["address"]["street"]
        if store["address"]["number"] and len(store["address"]["number"]) > 0:
            street_address = store["address"]["number"] + ", " + street_address

        city = store["address"]["city"]
        state = store["address"]["state"]
        zip = store["address"]["postalCode"]

        country_code = "CO"

        store_number = store["id"]
        page_url = page_url.format(
            location_name.replace(" ", "-").strip() + "-" + state + "-" + zip,
            store_number,
        )

        phone = store["instructions"]
        if phone and "Teléfono:" in phone:
            phone = phone.split("Teléfono:")[1].strip().split("-")[0].strip()
            if len(phone) == 3:
                phone = store["instructions"].split("Teléfono:")[1].strip()

        if phone == "null" or phone == "0":
            phone = "<MISSING>"

        location_type = "<MISSING>"
        hours_list = []
        weekdays_dict = {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
        }
        days_list = []
        if store["businessHours"]:
            hours = store["businessHours"]
            hours_list = []
            for hour in hours:
                day = weekdays_dict[hour["dayOfWeek"]]
                time = hour["openingTime"] + " - " + hour["closingTime"]
                days_list.append(day)
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["address"]["location"]["latitude"]
        longitude = store["address"]["location"]["longitude"]

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
