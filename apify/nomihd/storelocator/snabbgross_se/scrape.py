# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "snabbgross.se"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get("https://www.snabbgross.se/butik-sok", headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = json.loads(
            "".join(
                stores_sel.xpath('//input[@class="js-storefinder-stores"]/@value')
            ).strip()
        )["data"]
        for store in stores:

            store_number = store["name"]
            page_url = f"https://www.snabbgross.se/butik/{store_number}"
            locator_domain = website
            location_name = store["displayName"]
            street_address = store["line1"]
            if "line2" in store and store["line2"] is not None:
                street_address = street_address + ", " + store["line2"]

            city = store.get("town", "<MISSING>")
            state = "<MISSING>"
            zip = store.get("postalCode", "<MISSING>")
            country_code = "SE"

            phone = store.get("phone", "<MISSING>")
            location_type = "<MISSING>"
            if "öppnar i" in location_name:
                location_type = "Opening Soon"

            hours_dict = store.get("openings", {})
            hours_list = []
            for day in hours_dict.keys():
                time = hours_dict[day]
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = (
                store["latitude"],
                store["longitude"],
            )

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
