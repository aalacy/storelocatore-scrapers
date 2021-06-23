# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json


website = "thesalon.blue"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "thesalon.blue",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data = {"action": "location_data", "lat": "56.6898", "lng": "93.4545"}


def fetch_data():
    # Your scraper here
    api_url = "https://thesalon.blue/wp-admin/admin-ajax.php"
    api_res = session.post(api_url, headers=headers, data=data)

    json_res = json.loads(api_res.text)

    stores_list = json_res

    for store in stores_list:
        page_url = store["url"]

        store_number = store["id"]
        locator_domain = website

        location_name = store["location_name"].strip()
        street_address = (
            store["location_address"]["street_number"]
            + " "
            + store["location_address"]["street_name"]
        ).strip()

        city = store["location_address"]["city"].strip()
        state = store["location_address"]["state_short"].strip()

        zip = store["location_address"]["post_code"].strip()

        country_code = store["location_address"]["country_short"].strip()
        phone = store["phone_number"]
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = store["location_address"]["lat"]
        longitude = store["location_address"]["lng"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
