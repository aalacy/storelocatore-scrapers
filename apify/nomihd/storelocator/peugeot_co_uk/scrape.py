# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "peugeot.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.peugeot.co.uk",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.peugeot.co.uk/tools/find-a-retailer.html",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.peugeot.co.uk/apps/atomic/DealersServlet?distance=300&latitude=55.378051&longitude=-3.435973&maxResults=100&path=L2NvbnRlbnQvcGV1Z2VvdC93b3JsZHdpZGUvdWsvZW4%3D&searchType=latlong"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["payload"]["dealers"]
    for store in stores:
        page_url = store["dealerUrl"]

        locator_domain = website

        location_name = store["dealerName"]

        street_address = store["address"]["addressLine1"]

        city = store["address"]["cityName"]
        state = "<MISSING>"
        zip = store["address"]["postalCode"]

        country_code = "GB"

        store_number = "<MISSING>"

        phone = store["generalContact"]["phone1"]

        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if "generalOpeningHour" in store:
            hours_of_operation = "; ".join(
                store["generalOpeningHour"].split("<br />")
            ).strip()

        latitude = store["geolocation"]["latitude"]
        longitude = store["geolocation"]["longitude"]

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
