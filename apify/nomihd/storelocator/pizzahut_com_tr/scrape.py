# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "pizzahut.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "auth.pizzahut.com.tr",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9",
}


def fetch_data():
    # Your scraper here
    data = '{"Username":"robuser@clockwork.com.tr","Password":"7656BAF3F15A6504BBF3CEE829092DFA"}'

    auth_req = session.post(
        "https://auth.pizzahut.com.tr/api/auth/AuthService", headers=headers, data=data
    ).json()

    API_HEADERS = {
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://pizzahut.com.tr/",
        "Authorization": "Bearer " + auth_req["access_token"],
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    }

    search_url = (
        "https://api.pizzahut.com.tr/api/web/Restaurants/GetRestaurants?getAll=true"
    )

    stores_req = session.get(search_url, headers=API_HEADERS)
    stores = json.loads(stores_req.text)["result"]
    for store in stores:
        if store["isStoreActive"] is False:
            continue
        page_url = "https://pizzahut.com.tr/restoranlar"
        location_name = store["name"]
        location_type = "<MISSING>"
        locator_domain = website
        raw_address = store["address"]
        formatted_addr = parser.parse_address_intl(
            raw_address.rsplit("/", 1)[0].strip()
        )
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = raw_address.split("/")[-1].strip()
        state = store["townName"]
        zip = formatted_addr.postcode

        country_code = "TR"
        store_number = store["id"]
        phone = store["phone"]
        hours_list = []
        hours = store["storeWorkingTimes"]
        for hour in hours:
            if hour["dayOfWeek"] == 1:
                day = "Mon:"
            if hour["dayOfWeek"] == 2:
                day = "Tue:"
            if hour["dayOfWeek"] == 3:
                day = "Wed:"
            if hour["dayOfWeek"] == 4:
                day = "Thu:"
            if hour["dayOfWeek"] == 5:
                day = "Fri:"
            if hour["dayOfWeek"] == 6:
                day = "Sat:"
            if hour["dayOfWeek"] == 7:
                day = "Sun:"

            time = (
                hour["startTime"].split(" ", 1)[-1].strip()
                + " - "
                + hour["endTime"].split(" ", 1)[-1].strip()
            )
            hours_list.append(day + time)

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
            raw_address=raw_address,
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
