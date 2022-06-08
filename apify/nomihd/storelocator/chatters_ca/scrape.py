# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "chatters.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "sls-api-service.sweetiq-sls-production-east.sweetiq.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "x-api-key": "",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "origin": "https://locations.chatters.ca",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://locations.chatters.ca/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://locations.chatters.ca/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        json_text = (
            '{"features":[{"type":'
            + stores_req.text.split('"features":[{"type":')[1]
            .strip()
            .split("]}}]}")[0]
            .strip()
            + "]}}]}"
        )

        stores = json.loads(json_text)["features"]
        for store in stores:
            store_number = str(store["properties"]["id"])
            page_url = "https://locations.chatters.ca/" + store["properties"]["slug"]
            log.info(f"Pulling data for ID: {store_number}")
            store_req = session.get(
                "https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/7d0Vk88cVVHEpawHrS6e3bze3pbkWY/locations-details?locale=en_CA&ids="
                + store_number
                + "&clientId=5de977cea324c2c365a2576b&cname=locations.chatters.ca",
                headers=headers,
            )
            store_json = json.loads(store_req.text)["features"][0]
            latitude = store_json["geometry"]["coordinates"][1]
            longitude = store_json["geometry"]["coordinates"][0]

            location_name = store_json["properties"]["name"]

            locator_domain = website

            location_type = "<MISSING>"

            street_address = store_json["properties"]["addressLine1"]
            if (
                store_json["properties"]["addressLine2"] is not None
                and len(store_json["properties"]["addressLine2"]) > 0
            ):
                street_address = (
                    street_address + ", " + store_json["properties"]["addressLine2"]
                )

            city = store_json["properties"]["city"]
            state = store_json["properties"]["province"]
            zip = store_json["properties"]["postalCode"]
            country_code = store_json["properties"]["country"]
            phone = store_json["properties"]["phoneLabel"]
            hours_of_operation = ""
            hours_list = []
            hours = store_json["properties"]["hoursOfOperation"]
            for day in hours.keys():
                time = ""
                if len(hours[day]) > 0:
                    time = str(hours[day][0][0]) + "-" + str(hours[day][0][1])
                else:
                    time = "Closed"

                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            if store_json["properties"]["isPermanentlyClosed"] is not True:
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
