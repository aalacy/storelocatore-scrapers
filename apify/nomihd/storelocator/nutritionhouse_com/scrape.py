# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "nutritionhouse.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.nutritionhouse.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.nutritionhouse.com/Locations.aspx",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.nutritionhouse.com/WS/StoreLocator.asmx/getLocations"
    data = {"searchType": "ip", "searchTerm": "", "pageNo": 0}
    stores_req = session.post(search_url, json=data, headers=headers)
    stores = json.loads(stores_req.text)["d"]["data"]

    for store in stores:
        locator_domain = website
        page_url = "https://www.nutritionhouse.com/" + store["slug"]
        location_name = store["storeName"]

        street_address = store["addressLine1"]
        if (
            "addressLine2" in store
            and store["addressLine2"] is not None
            and len(store["addressLine2"]) > 0
        ):
            street_address = street_address + ", " + store["addressLine2"]
        city = store["city"]
        state = store["province"]
        zip = store["postalCode"]

        country_code = "CA"
        phone = store["phoneNumber"]

        store_number = store["storeNo"]
        location_type = "<MISSING>"

        hours_of_operation = ""
        hours = store["storeHours"]
        hours_list = []
        for hour in hours:
            if hour["closed"] is False:
                day = hour["title"]
                time = (
                    str(hour["openHour"])
                    + ":"
                    + str(hour["openMinute"])
                    + "0-"
                    + str(hour["closeHour"])
                    + ":"
                    + str(hour["closeMinute"])
                    + "0"
                )
                hours_list.append(day + ":" + time)
            else:
                day = hour["title"]
                hours_list.append(day + ":Closed")

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["coordinates"]["Latitude"]
        longitude = store["coordinates"]["Longitude"]

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
