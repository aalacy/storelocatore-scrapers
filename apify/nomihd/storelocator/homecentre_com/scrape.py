# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "homecentre.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.homecentre.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://www.homecentre.com/sa/en/storelocator",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

params = {
    "concept": "HOMECENTRE",
}


def fetch_data():
    # Your scraper here

    urls = [
        "https://www.homecentre.com/sa/en/storelocator/",
        "https://www.homecentre.com/ae/en/storelocator/",
        "https://www.homecentre.com/bh/en/storelocator/",
        "https://www.homecentre.com/kw/en/storelocator/",
        "https://www.homecentre.com/om/en/storelocator/",
        "https://www.homecentre.com/eg/en/storelocator/",
        "https://www.homecentre.com/qa/en/storelocator/",
    ]
    with SgRequests() as session:
        for search_url in urls:
            log.info(search_url)
            search_res = session.get(
                search_url.replace("/storelocator/", "/store-locator/"),
                headers=headers,
                params=params,
            )
            stores = json.loads(search_res.text)
            for store in stores:
                page_url = search_url
                locator_domain = website

                location_name = store["displayName"]

                street_address = store["address"]["line1"]

                city = store["address"]["region"]["name"]
                street_address = street_address.split(", " + city)[0].strip()
                state = "<MISSING>"
                zip = store["address"]["postalCode"]

                country_code = store["address"]["country"]["isocode"]

                store_number = store["rmsStoreCode"]
                phone = store["address"]["phone"]

                location_type = "<MISSING>"

                hours_of_operation = store["workingHours"]

                latitude = store["geoPoint"]["latitude"]
                longitude = store["geoPoint"]["longitude"]

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
