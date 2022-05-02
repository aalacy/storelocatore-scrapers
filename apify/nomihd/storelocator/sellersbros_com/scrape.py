# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sellersbros.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://sellersbros.com/locations/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//div[@data-block-json]")

        stores_details = search_sel.xpath(
            '//main//div[@class="sqs-block-content" and p]'
        )

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url

            store_info = json.loads("".join(store.xpath("./@data-block-json")))[
                "location"
            ]

            location_name = store_info.get("addressTitle", "SellerBros")
            location_type = "<MISSING>"

            raw_address = "<MISSING>"
            full_address = (
                store_info["addressLine1"] + " " + store_info["addressLine2"]
            ).strip()

            phone_hours_info = []
            for store_details in stores_details:
                phone_hours_info = list(
                    filter(
                        str,
                        [x.strip() for x in store_details.xpath(".//text()")],
                    )
                )

                if (
                    phone_hours_info[0] in full_address
                    or phone_hours_info[1].split(" ")[-1] in full_address
                ):

                    break

            street_address = " ".join(full_address.split(",")[0].strip().split(" "))[
                :-1
            ]

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            city = full_address.split(",")[0].strip().split(" ")[-1]

            state = full_address.split(" ")[-2].strip(", ")
            zip = full_address.split(" ")[-1]

            country_code = "US"

            store_number = "<MISSING>"
            if "#" in location_name:
                store_number = location_name.split("#")[1].strip()
            phone = phone_hours_info[2]

            hours = phone_hours_info[3:]

            hours_of_operation = (
                "; ".join(hours)
                .replace("day;", "day:")
                .replace("b;", "b:")
                .replace("Dia:; ", "")
                .replace("Hora:; ", "")
                .strip()
            )

            latitude, longitude = store_info["markerLat"], store_info["markerLng"]

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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
