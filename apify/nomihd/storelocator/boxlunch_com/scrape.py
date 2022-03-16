# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "boxlunch.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.boxlunch.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.boxlunch.com/on/demandware.store/Sites-boxlunch-Site/default/Stores-GetNearestStores?postalCode=10001&customStateCode=&maxdistance=50000&unit=mi&latitude=37.0902&longitude=95.7129&maxResults=1500&distanceUnit=mi&countryCode=US&productId=null&currentStoreId=null&pageSource=null"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads("".join(stores_req.text).strip())["stores"]

    for key in stores.keys():
        locator_domain = website
        page_url = "https://www.boxlunch.com/stores-details?StoreID=" + key
        location_name = stores[key]["name"]

        street_address = stores[key]["address1"]
        if (
            "address2" in stores[key]
            and stores[key]["address2"] is not None
            and len(stores[key]["address2"]) > 0
        ):
            street_address = street_address + ", " + stores[key]["address2"]
        city = stores[key]["city"]
        state = stores[key]["stateCode"]
        zip = stores[key]["postalCode"]

        country_code = stores[key]["countryCode"]
        phone = stores[key]["phone"]

        store_number = key
        location_type = "<MISSING>"

        hours_of_operation = ""
        hours_list = []

        if stores[key]["storeHours"] is not None and len(stores[key]["storeHours"]) > 0:
            hours_sel = lxml.html.fromstring(stores[key]["storeHours"])
            hours = hours_sel.xpath('//div[@class="hours-row"]')
            for hour in hours:
                day = "".join(
                    hour.xpath('span[@class="store-hours-day"]/text()')
                ).strip()
                time = "".join(
                    hour.xpath('span[@class="store-hours-time"]/text()')
                ).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = stores[key]["latitude"]
        longitude = stores[key]["longitude"]

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
