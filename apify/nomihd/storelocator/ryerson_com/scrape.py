# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ryerson.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    urls = [
        "https://www.ryerson.com/en/locations/unitedstates",
        "https://www.ryerson.com/en/locations/canada",
    ]

    with SgRequests() as session:
        for url in urls:
            search_url = url
            stores_req = session.get(search_url, headers=headers)
            stores = json.loads(
                stores_req.text.split("var plantInfo = ")[1]
                .strip()
                .split("];")[0]
                .strip()
                + "]"
            )

            for store in stores:
                page_url = "<MISSING>"
                if store["SCURL"]:
                    page_url = "https://www.ryerson.com" + store["SCURL"]

                if (
                    "unitedstates" in page_url or "canada" in page_url
                ) or page_url == "<MISSING>":
                    locator_domain = website
                    location_name = store["PlantPublicName"]
                    street_address = store["PlantStreet"]
                    city = store["PlantCity"]
                    state = store["PlantState"]
                    zip = store["ZipCode"]

                    country_code = "<MISSING>"
                    if "unitedstates" in search_url:
                        country_code = "US"
                    elif "canada" in search_url:
                        country_code = "CA"

                    store_number = str(store["Id"])
                    phone = store["MainPhone"]

                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"

                    latitude = store["lat"]
                    longitude = store["lon"]

                    if (phone == "" or phone is None) and page_url != "<MISSING>":
                        log.info(page_url)
                        store_req = session.get(page_url, headers=headers)
                        store_sel = lxml.html.fromstring(store_req.text)
                        phone = "".join(
                            store_sel.xpath('//div[@itemprop="telephone"]/text()')
                        ).strip()

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
