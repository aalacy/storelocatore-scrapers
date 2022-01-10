# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "wendys.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "wendys.cl",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://wendys.cl/locales"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        json_text = (
            "".join(
                stores_sel.xpath(
                    "//div[@data-maps-collection-value]/@data-maps-collection-value"
                )
            )
            .strip()
            .replace("&quot;", '"')
        )
        regions = json.loads(json_text)
        for region in regions.keys():
            stores = regions[region]
            for store in stores:
                page_url = search_url

                locator_domain = website
                location_name = store["name"]
                street_address = store["address1"]
                city = store["city"]
                if city == "PUENTE ALTO /CALLE CAMILO HENRIQUEZ 3692,2 NIVEL":
                    city = "PUENTE ALTO"
                    street_address = "CALLE CAMILO HENRIQUEZ 3692,2 NIVEL"
                state = store["state_name"]
                zip = "<MISSING>"

                country_code = "CL"

                store_number = store["id"]
                phone = store["phone"]
                if phone and phone == "0":
                    phone = "<MISSING>"

                location_type = "<MISSING>"

                latitude = store["lat"]
                longitude = store["lng"]

                hours_of_operation = "<MISSING>"

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
