# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahutdelivery.ro"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahutdelivery.ro",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahutdelivery.ro/ro/contact/locatii"
    search_req = session.get(search_url, headers=headers)
    json_str = (
        search_req.text.split(':locations="')[1]
        .strip()
        .split('}]}"')[0]
        .strip()
        .replace("&quot;", '"')
        .strip()
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        + "}]}"
    )
    locations = json.loads(json_str)
    cities = json.loads(
        (
            search_req.text.split(':cities-with-locations="')[1]
            .strip()
            .split('}]"')[0]
            .strip()
            .replace("&quot;", '"')
            .strip()
            + "}]"
        )
    )
    cities_dict = {}
    for city in cities:
        cities_dict[city["cityId"]] = city["name"]

    for key in locations.keys():
        stores = locations[key]
        for store in stores:
            page_url = "https://www.pizzahutdelivery.ro/ro/contact/locatii"

            locator_domain = website

            location_name = store["name"]

            street_address = store["address"]
            if street_address is None or len(street_address) <= 0:
                continue
            city = cities_dict[str(store["cityId"])]

            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "RO"

            phone = store["phone"]

            store_number = store["id"]

            location_type = "<MISSING>"

            hours_of_operation = "; ".join(store["deliverySchedule"].split(",<br />"))

            latitude = store["coordinates"].split(",")[0].strip()
            longitude = store["coordinates"].split(",")[-1].strip()

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
