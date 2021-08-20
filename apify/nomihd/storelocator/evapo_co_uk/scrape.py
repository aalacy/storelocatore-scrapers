# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "evapo.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "evapo.co.uk",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://evapo.co.uk",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://evapo.co.uk/vape-shops/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://evapo.co.uk/amlocator/index/ajax/"
    data = {
        "lat": "",
        "lng": "",
        "radius": "",
        "mapId": "amlocator-map-canvas60355f8b6642e",
        "storeListId": "amlocator_store_list60355f8b64aea",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
        "p": "ajax",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["items"]
    for store in stores:
        page_url = store["canonical_url"]

        location_type = "<MISSING>"
        location_name = store["name"]

        locator_domain = website

        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip = store["zip"]
        country_code = store["country"]

        phone = store["phone"]

        hour_list = []

        hours = json.loads(store["schedule_string"].replace('"', '"'))
        for day in hours.keys():
            if hours[day][day + "_status"] == "1":
                time = (
                    hours[day]["from"]["hours"]
                    + ":"
                    + hours[day]["from"]["minutes"]
                    + "-"
                    + hours[day]["to"]["hours"]
                    + ":"
                    + hours[day]["to"]["minutes"]
                )
            elif hours[day][day + "_status"] == "0":
                time = "Closed"

            hour_list.append(day + ":" + time)

        hours_of_operation = ";".join(hour_list).strip()

        store_number = store["id"]

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
