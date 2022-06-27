# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.fridayschile.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "api.getjusto.com",
    "x-orion-pathname": "/local",
    "x-orion-domain": "www.fridayschile.cl",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "content-type": "application/json",
    "accept": "*/*",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.fridayschile.cl",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (("operationName", "getWebsitePage_cached"),)

data = '{"operationName":"getWebsitePage_cached","variables":{"pageId":"khdcXxsAFbdZpLxkg","websiteId":"EPYnKRcfQK4osvmwx"},"query":"query getWebsitePage_cached($pageId: ID, $websiteId: ID) {\\n  page(pageId: $pageId, websiteId: $websiteId) {\\n    _id\\n    path\\n    activeComponents {\\n      _id\\n      options\\n      componentTypeId\\n      schedule {\\n        isScheduled\\n        latestScheduleStatus\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'


def fetch_data():
    # Your scraper here
    search_url = "https://www.fridayschile.cl/local"
    api_url = "https://api.getjusto.com/graphql"

    with SgRequests() as session:
        global params
        global data
        api_res = session.post(api_url, headers=headers, params=params, data=data)
        json_res = json.loads(api_res.text)

        stores = json_res["data"]["page"]["activeComponents"]
        for target in stores:
            if target["componentTypeId"] == "stores":
                stores = target["options"]["stores"]

        for _, store in enumerate(stores, 1):

            page_url = search_url

            locator_domain = website

            location_name = store["name"].strip()
            phone = store["phone"]

            #  To get location details
            store_number = store["placeId"]
            params = (("operationName", "getPlaceDetails_cached"),)
            data = '{"operationName":"getPlaceDetails_cached","variables":{"placeId":"PLACE_ID"},"query":"query getPlaceDetails_cached($placeId: ID) {\\n  place(placeId: $placeId) {\\n    _id\\n    text\\n    secondaryText\\n    location\\n    __typename\\n  }\\n}\\n"}'.replace(
                "PLACE_ID", store_number
            )

            api_res = session.post(api_url, headers=headers, params=params, data=data)
            json_res = json.loads(api_res.text)

            store_info = json_res["data"]["place"]

            raw_address = "<MISSING>"

            street_address = store_info["text"]

            city = store_info["secondaryText"].split(",")[0].strip()
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = store_info["secondaryText"].split(",")[1].strip()

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store_info["location"]["lat"],
                store_info["location"]["lng"],
            )

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
