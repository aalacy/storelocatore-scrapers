# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "ramen-yamadaya.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.ramen-yamadaya.com",
    "accept": "*/*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "origin": "https://www.ramen-yamadaya.com",
    "referer": "https://www.ramen-yamadaya.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    with SgRequests() as session:
        js_req = session.get(
            "https://www.ramen-yamadaya.com/webpack/production/consumer-bundle.modern_consumer.84c4abe37cb67d1980f6.js",
            headers=headers,
        )
        ID = (
            js_req.text.split('"restaurantWithLocations":"')[1]
            .strip()
            .split('"')[0]
            .strip()
        )
        log.info(ID)

        json_data = {
            "operationName": "restaurantWithLocations",
            "variables": {
                "restaurantId": 12468,
            },
            "extensions": {
                "operationId": "PopmenuClient/" + ID,
            },
        }
        stores_req = session.post(
            "https://www.ramen-yamadaya.com/graphql", headers=headers, json=json_data
        )
        stores = json.loads(stores_req.text)["data"]["restaurant"]["locations"]

        for store in stores:

            locator_domain = website

            location_name = store["name"]
            if "downtown-los-angeles" == store["slug"]:
                page_url = "https://www.ramen-yamadaya.com/menu-dtla"
            else:
                page_url = "https://www.ramen-yamadaya.com/" + store["slug"]

            location_type = "<MISSING>"

            street_address = store["streetAddress"]
            city = store["city"]
            state = store["state"]
            zip = store["postalCode"]

            country_code = "US"

            phone = store["displayPhone"]

            hours = store["schemaHours"]
            hours_dict = {}
            for hour in hours:
                day = hour.split(" ", 1)[0].strip()
                curr_time = hour.split(" ", 1)[1].strip()
                if day in hours_dict:
                    time = hours_dict[day]
                    hours_dict[day] = curr_time + ", " + time
                else:
                    hours_dict[day] = curr_time

            hours_list = []
            for dy in hours_dict:
                hours_list.append(dy + ":" + hours_dict[dy])

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = store["id"]
            latitude, longitude = store["lat"], store["lng"]

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
