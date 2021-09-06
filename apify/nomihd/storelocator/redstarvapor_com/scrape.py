# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "redstarvapor.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.redstarvapor.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.redstarvapor.com/locations/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.redstarvapor.com/wp-admin/admin-ajax.php?action=store_search&lat=33.44838&lng=-112.07404&max_results=25&search_radius=50&autoload=1"

    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = store["permalink"]
        locator_domain = website
        location_name = store["store"].replace("&#038;", "&")
        street_address = store["address"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        if ",," in street_address:
            street_address = street_address.replace(",,", ",").strip()

        city = store["city"].replace(",", "").strip()
        state = store["state"]
        zip = store["zip"]

        country_code = store["country"]

        store_number = str(store["id"])
        phone = store["phone"]

        location_type = "<MISSING>"
        hours_list = []
        if store["hours"] is not None and len(store["hours"]) > 0:
            hours = lxml.html.fromstring(store["hours"]).xpath("//tr")
            hours_list = []
            hours_of_operation = ""
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]//text()")).strip()
                hours_list.append(day + ":" + time)

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
