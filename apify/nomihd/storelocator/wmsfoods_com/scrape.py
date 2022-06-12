# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "wmsfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "wmsfoods.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "origin": "https://wmsfoods.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://wmsfoods.com/contact",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://wmsfoods.com/ajax/index.php"
    data = {}
    data["method"] = "POST"
    data[
        "apiurl"
    ] = "https://wmsfoods.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1"

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["GetClientStores"]

    for store in stores:
        page_url = "https://wmsfoods.com/contact"
        locator_domain = website
        location_name = store["ClientStoreName"]
        street_address = store["AddressLine1"]
        city = store["City"]
        state = store["StateName"]
        zip = store["ZipCode"]

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = store["StoreNumber"]
        phone = store["StorePhoneNumber"]

        location_type = "<MISSING>"

        hours_of_operation = store["StoreTimings"]

        latitude = store["Latitude"]
        longitude = store["Longitude"]

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
