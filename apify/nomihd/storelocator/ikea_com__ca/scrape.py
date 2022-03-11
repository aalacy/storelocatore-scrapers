# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "ikea.com/ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://cat-tool.ikea-canada.ca/api/postal-codes/get_locations/en/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        stores = json.loads(search_res.text)

        for key in stores.keys():

            if stores[key]["type"] == "DS" or stores[key]["type"] == "CP":
                continue
            page_url = "https://www.ikea.com" + stores[key]["lsp_url"]
            locator_domain = website

            location_name = stores[key]["location_name"]
            if location_name == "Outside Market Area":
                continue
            street_address = stores[key]["address"]
            city = stores[key]["city"]
            state = stores[key]["prov"]
            zip = stores[key]["postal"]
            country_code = "CA"

            phone = "1-866-866-4532"
            store_number = "<MISSING>"

            location_type = "<MISSING>"
            if "temporarily closed" in stores[key]["location_notes"]:
                location_type = "temporarily closed"
            hours = stores[key]["hours"]
            hours_list = []
            for hour in hours:
                day = hour["day"]
                if day == "any":
                    continue
                time = hour["open_time"] + " - " + hour["close_time"]
                hours_list.append(day + ": " + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = stores[key]["lat"]
            longitude = stores[key]["long"]

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
