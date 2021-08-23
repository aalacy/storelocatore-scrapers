# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.cw"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "fb.tictuk.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://cdn.tictuk.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://cdn.tictuk.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    data = '{"chainId":"3665184690713015","type":"getBranchesList","cust":"openRest","lang":"en"}'

    search_req = session.post(
        "https://fb.tictuk.com/webFlowAddress", headers=headers, data=data
    )
    stores = json.loads(search_req.text)["msg"]["pickupStores"]
    for store in stores:

        req_ID = (
            session.get(
                f"https://fb.tictuk.com/start_web_session?cust=openRest&store={store['id']}&user=d8f30de5-b943-4d39-a214-68e2ff12bff4&lang=en&ref=%7B%22ref%22%3A%22chainWeb%22%2C%22orderType%22%3A%22peakup%22%7D&chain=3665184690713015",
                headers=headers,
            )
            .text.split("request=")[1]
            .strip()
            .split("&")[0]
            .strip()
        )
        store_req = session.get(
            f"https://fb.tictuk.com/check_field?cust=openRest&request={req_ID}&field=getStore&value=",
            headers=headers,
        )
        store_json = json.loads(store_req.text)["msg"]
        locator_domain = website

        location_name = store_json["name"]["en_US"]
        street_address = store_json["address"]["formatted"]
        state = "<MISSING>"
        city = store_json["address"]["city"]
        zip = "<MISSING>"

        country_code = "CW"

        phone = store_json["phoneNumber"]
        store_number = store_json["id"]

        page_url = "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = store_json["address"]["latLng"]["lat"]
        longitude = store_json["address"]["latLng"]["lng"]

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
