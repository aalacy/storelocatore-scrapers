# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import time


website = "davisfoodanddrug.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "davisfoodanddrug.com",
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
    api_url = f"https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackHours&action=storeInfo&website_url=davisfoodanddrug.com&expandedHours=true&_={round(time.time() * 1000)}"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text.replace("jsonpcallbackHours(", "").strip(") "))

    stores_list = json_res

    for store in stores_list:
        for store_dep in store:
            if store_dep["store_department_name"] != "Store":
                continue

        page_url = "https://davisfoodanddrug.com/" + store_dep[
            "store_city"
        ].lower().strip().replace(" ", "_")

        store_number = store_dep["store_id"]
        locator_domain = website

        location_name = store_dep["store_name"]

        street_address = store_dep["store_address"].strip()

        city = store_dep["store_city"].strip()
        state = store_dep["store_state"].strip()

        zip = store_dep["store_zip"].strip()

        country_code = "US"
        phone = store_dep["store_phone"]

        location_type = "<MISSING>"

        hours = []
        for day in [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]:
            hours.append(f"{day}: {store_dep[day]}")
        hours_of_operation = "; ".join(hours).replace("Closed to Closed", "Closed")

        latitude = store_dep["store_lat"]
        longitude = store_dep["store_lat"]

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
