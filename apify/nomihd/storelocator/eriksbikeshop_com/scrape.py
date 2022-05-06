# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "eriksbikeshop.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.eriksbikeshop.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "*/*",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.eriksbikeshop.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.eriksbikeshop.com/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    home_req = session.get("https://www.eriksbikeshop.com/stores", headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    json_str = "".join(
        home_sel.xpath('//template[@data-varname="__RUNTIME__"]/script/text()')[0]
    ).strip()
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
    search_url = "https://www.eriksbikeshop.com/_v/private/graphql/v1"
    params = (
        ("workspace", "master"),
        ("maxAge", "long"),
        ("appsEtag", "remove"),
        ("domain", "store"),
        ("locale", "en-US"),
        ("__bindingId", "7b5f460a-f478-46aa-ac11-0ae4867af27f"),
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
    stores_req = session.post(
        search_url, headers=headers, params=params, data=json.dumps(data)
    )
    stores = json.loads(stores_req.text)["data"]["getStores"]["items"]

    for store in stores:
        page_url = "https://www.eriksbikeshop.com/store/{}/{}"
        locator_domain = website
        location_name = store["name"]
        street_address = store["address"]["street"]
        if store["address"]["number"] and len(store["address"]["number"]) > 0:
            street_address = store["address"]["number"] + " " + street_address

        city = store["address"]["city"]
        state = store["address"]["state"]
        zip = store["address"]["postalCode"]

        country_code = "US"

        store_number = store["id"]
        page_url = page_url.format(
            city.replace(" ", "-").strip() + "-" + state + "-" + zip, store_number
        )

        phone = store["instructions"]

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

        for day in weekdays_dict.values():
            if day not in days_list:
                hours_list.append(day + ":Closed")

        hours_of_operation = "; ".join(hours_list).strip()
        if hours_of_operation.count("Closed") == 7:
            continue
        latitude = str(store["address"]["location"]["latitude"])
        longitude = str(store["address"]["location"]["longitude"])

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
