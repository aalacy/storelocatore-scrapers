# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "lego.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.lego.com",
    "accept": "*/*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InB1YiI6e30sInB2dCI6InRmVC9ZRUFyRng5WW0xWDJxeStabGpZUnZQVm50am1XQnhmNkc0TW01dTRGRk80bDlYRUFNMnhTeUNaNFZrZUpxdE1obW1Sa1FrZnRvOE9aTmJ6eWg1T0lPK3dKQlBIOGtISHlRL2VERFRzR0FyNGhZL3N1cGpVUDRTWDhJcUU3RkZORjFIcTE5YzVkTFRValZuZTExNHFoWTVweHdYTFh6Mk5oMHliUGd1UHJSUXZvYnhSN1NPNW9aM2RDVU0xSmk4anV4dU5FdW15MktNN2EvYUdZeEhrc0g5Undmd1VWcDQ1ZlBUV1RrU3Y2dkRaR0dvL3V4eWppaVV6cS9kSVMrbzd3QWNwa25CZ29SWnRFZmdKQzQ5aURZSWl1VE1IQ2FoUXlIbWNPUGJldDhFYWdvNXdNNFV0YUQwTGE3LzhoOHY2SVdRSnZOWkh0aWtLdVFCcGRXaGx2aE5RejF5ZlE5UWhCVWdlUGtSbnpKSmc4RklzZlQyaSs1eGx1cXo1V0dhUmdqRi81Y2g2Z2hZUzJ0MjcydU4zWlFxLzcvUm1tVDRla2V3WmY3NW1Lczl0MitOd3poTVBIVkEyNkFOckE2MXF6dzdLUkFLZGdIUjV1U0NtdTZiZDFlc0xjQkNRcjFWcytzSm1tVlJyYXJ3SUxBUUxiVkFsVnM0LyswWTVPMzVjRXNEeUo5NzIxS0ZJb2lpbHBOTkFtd3hLcEszNGM5K1JsZm93d3hTWjZEaVpzZzZwWElrdHNBZ015d0VJMC5xRDdGa2NsZzdTVTZrZVhjUExGenBnPT0ifSwiaWF0IjoxNjUyMzU3MTgxLCJleHAiOjE2NTIzNjc5ODF9.KV4utlbZz73o9Z38rWeJcXxssV-osckDK0Mqf9Mg7vs",
    "features": "rewardsCenter=false",
    "origin": "https://www.lego.com",
    "referer": "https://www.lego.com/en-us/stores/directory",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "same-origin",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "x-locale": "en-US",
}


json_data = {
    "operationName": "StoresDirectory",
    "variables": {},
    "query": "query StoresDirectory {\n  storesDirectory {\n    id\n    country\n    region\n    stores {\n      storeId\n      name\n      phone\n      state\n      phone\n      openingDate\n      certified\n      additionalInfo\n      storeUrl\n      urlKey\n      isNewStore\n      isComingSoon\n      __typename\n    }\n    __typename\n  }\n}\n",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.lego.com/api/graphql/StoresDirectory"
    stores_req = session.post(search_url, json=json_data, headers=headers)
    regions = json.loads(stores_req.text)["data"]["storesDirectory"]
    for region in regions:
        country_code = region["country"]
        stores = region["stores"]
        for store in stores:
            locator_domain = website
            store_json_data = {
                "operationName": "StoreInfo",
                "variables": {
                    "urlKey": store["urlKey"],
                },
                "query": "query StoreInfo($urlKey: String!) {\n  storeInfo(urlKey: $urlKey) {\n    storeId\n    name\n    phone\n    openingTimes {\n      day\n      timeRange\n      __typename\n    }\n    coordinates {\n      lat\n      lng\n      __typename\n    }\n    storeUrl\n    urlKey\n    streetAddress\n    city\n    postalCode\n    state\n    region\n    openingDate\n    certified\n    additionalInfo\n    isNewStore\n    isComingSoon\n    storeFeatures\n    events {\n      ...StoreEventsDetail\n      __typename\n    }\n    description\n    storeImage {\n      small {\n        ...ImageAsset\n        __typename\n      }\n      large {\n        ...ImageAsset\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment StoreEventsDetail on StoreEvent {\n  urlKey\n  heading\n  subHeading\n  thumbnailImage {\n    small {\n      ...ImageAsset\n      __typename\n    }\n    large {\n      ...ImageAsset\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ImageAsset on ImageAssetDetails {\n  url\n  width\n  height\n  maxPixelDensity\n  format\n  __typename\n}\n",
            }

            store_req = session.post(
                "https://www.lego.com/api/graphql/StoreInfo",
                headers=headers,
                json=store_json_data,
            )
            store_info = json.loads(store_req.text)["data"]["storeInfo"]
            location_name = store_info["name"]
            log.info(location_name)
            page_url = (
                store_info["storeUrl"]
                .replace("/stores/stores/", "/stores/store/")
                .strip()
            )

            street_address = store_info["streetAddress"]
            if street_address:
                raw_address = street_address

            city = store_info["city"]
            if city:
                raw_address = raw_address + ", " + city

            state = store_info["state"]
            if state:
                raw_address = raw_address + ", " + state

            zip = store_info["postalCode"]
            if zip:
                raw_address = raw_address + ", " + zip

            store_number = "<MISSING>"
            phone = store_info["phone"]
            if phone and phone == "v":
                phone = "<MISSING>"

            location_type = "<MISSING>"
            hours = store_info["openingTimes"]
            hours_list = []
            for hour in hours:
                hours_list.append(hour["day"] + ":" + hour["timeRange"])

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store_info["coordinates"]["lat"]
            longitude = store_info["coordinates"]["lng"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
