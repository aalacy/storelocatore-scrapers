# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "rebath.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.rebath.com",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "accept": "text/html, */*; q=0.01",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "origin": "https://www.rebath.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.rebath.com/rebath-locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.rebath.com/modules/multilocation/?near_location=10001&threshold=120000&s[…]ces__in=&published=1&within_business=true&offset=0&limit=1000"
    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    stores_list = json_res["objects"]

    for store in stores_list:

        page_url = store["location_url"]
        locator_domain = website

        location_name = store["location_name"]

        street_address = store["street"]
        if store["street2"] in store and store["street2"] is not None:
            street_address = (
                (street_address + ", " + store["street2"]).strip(" ,").strip()
            )

        city = store["city"]
        state = store["state"]
        zip = store["postal_code"]

        country_code = store["country"]

        store_number = store["id"]

        phone = store["phones"][0]["number"]

        location_type = "<MISSING>"

        hours = store["formatted_hours"]["primary"]["days"]
        hour_list = []
        for hour in hours:
            day = hour["label"]
            timing = hour["content"]
            hour_list.append(f"{day}: {timing}")

        hours_of_operation = (
            "; ".join(hour_list) if hour_list.count("Closed") < 7 else "<MISSING>"
        )

        latitude = store["lat"]
        longitude = store["lon"]

        raw_address = "<MISSING>"
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
