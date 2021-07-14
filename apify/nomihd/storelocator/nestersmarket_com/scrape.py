# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "nestersmarket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.nestersmarket.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.kellysroastbeef.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://www.nestersmarket.com"
    api_url = "https://storeportal.buy-low.com/wp-admin/admin-ajax.php/admin-ajax.php?action=buylow_get_store_list&banner=nesters-market&timezone="
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res

    for store in stores_list:

        page_url = base + store["page_url"]

        store_number = store["storeNumber"]
        locator_domain = website

        location_name = store["storeName"]
        store_info = store["store_details"]

        street_address = store_info["address"].strip()
        city = store_info["city"].strip()
        state = store_info["province"].strip()

        zip = store_info["postal_code"].strip()

        country_code = "CA"
        phone = store_info["phone_numbers"][0]["phone_number"]

        location_type = "<MISSING>"

        hours_info = store["store_hours"]
        hours = []
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            opens = hours_info[day]["start"]
            closes = hours_info[day]["Close"]
            hours.append(f"{day}: {opens}-{closes}")
        hours_of_operation = "; ".join(hours)

        latitude = store["map_data"]["latitude"]
        longitude = store["map_data"]["longitude"]

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
