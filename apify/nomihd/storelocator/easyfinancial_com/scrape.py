# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "easyfinancial.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.easyfinancial.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.easyfinancial.com/find-branch",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.easyfinancial.com/store-list/info.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["store_list"]

    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["storeName"]
        street_address = store["address"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store["city"]
        state = store["province"]
        if "-" in state:
            state = state.split("-")[0].strip()

        zip = store["postalCode"]

        country_code = store["country"]

        store_number = store["storeCode"]
        phone = store["storePhone"]

        location_type = store["storeType"]

        hours_list = []
        try:
            temp_hours = (
                "Mon-Fri:"
                + store["weekdayOpen"][:2]
                + ":"
                + store["weekdayOpen"][2:]
                + "-"
                + store["weekdayClose"][:2]
                + ":"
                + store["weekdayClose"][2:]
            )
            hours_list.append(temp_hours)
        except:
            pass

        try:
            temp_hours = (
                "Sat:"
                + store["saturdayOpen"][:2]
                + ":"
                + store["saturdayOpen"][2:]
                + "-"
                + store["saturdayClose"][:2]
                + ":"
                + store["saturdayClose"][2:]
            )
            hours_list.append(temp_hours)
        except:
            pass

        try:
            temp_hours = (
                "Sun:"
                + store["sundayOpen"][:2]
                + ":"
                + store["sundayOpen"][2:]
                + "-"
                + store["sundayClose"][:2]
                + ":"
                + store["sundayClose"][2:]
            )
            hours_list.append(temp_hours)
        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store["lat"]
        longitude = store["lng"]

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
