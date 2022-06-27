# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "ashleystewart.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

params = {
    "showMap": "true",
    "radius": "999999 mile radius",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://www.ashleystewart.com/on/demandware.store/Sites-AshleyStewart-Site/default/Stores-FindStores",
            headers=headers,
            params=params,
        )

        stores = json.loads(stores_req.text)["storesModel"]["stores"]
        for store in stores:
            page_url = (
                "https://www.ashleystewart.com/on/demandware.store/Sites-AshleyStewart-Site/default/Stores-Details?storeId="
                + store["ID"]
            )

            locator_domain = website
            location_name = store["name"]

            street_address = store["address1"]
            if (
                "address2" in store
                and store["address2"] is not None
                and len(store["address2"]) > 0
            ):
                street_address = street_address + ", " + store["address2"]

            city = store["city"]
            state = store["stateCode"]
            zip = store["postalCode"]

            country_code = store["countryCode"]

            store_number = page_url.split("?storeId=")[1].strip().split("-")[0].strip()
            phone = store["phone"]

            location_type = "<MISSING>"
            if "TEMPORARILY CLOSED" in store["storeHours"]:
                location_type = "TEMPORARILY CLOSED"

            if "storeHoursJSON" in store:
                hours = store["storeHoursJSON"]
                hours_list = []
                for hour in hours:
                    day = hour["dayofweek"].replace(".", "").strip()
                    time = hour["hourStr"]
                    hours_list.append(day + ":" + time)

                hours_of_operation = "; ".join(hours_list).strip()
            else:
                hours_sel = lxml.html.fromstring(store["storeHours"])
                hours_of_operation = "; ".join(
                    list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in hours_sel.xpath("//p[not(@class)]/text()")
                            ],
                        )
                    )
                ).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]

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
