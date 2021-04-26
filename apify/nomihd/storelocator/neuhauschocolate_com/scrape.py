# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "neuhauschocolate.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "us.neuhauschocolates.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://us.neuhauschocolates.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    url = "https://us.neuhauschocolates.com/on/demandware.store/Sites-Neuhaus-Webshop-US-Site/en_US/Stores-FindStores?showMap=false&radius=30000mi&postalCode=10001&radius=30000mi"
    stores_req = session.get(
        url,
        headers=headers,
    )
    stores = json.loads(stores_req.text.strip())["stores"]
    for store in stores:
        locator_domain = website
        location_name = store["name"]
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]
        city = store["city"]
        state = store["stateCode"]
        zip = store["postalCode"]
        country_code = store["countryCode"]
        page_url = "<MISSING>"
        phone = store["phone"]
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_list = []
        hours_of_operation = ""
        for key in store.keys():
            if "openingHours" in key:
                day = key.replace("openingHours", "").strip()
                hour_json = store[key].replace("\n", "").replace('\\"', '"').strip()
                time = ""
                if "CLOSED" in hour_json.upper():
                    time = "CLOSED"
                else:
                    time = (
                        json.loads(hour_json)["open"]
                        + "-"
                        + json.loads(hour_json)["close"]
                    )

                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

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
