# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hardings.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.hardings.com/store-information/find-your-store/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            "["
            + stores_req.text.split("var stores = [")[1].strip().split("}];")[0].strip()
            + "}]"
        )

        for store in stores:
            page_url = search_url

            locator_domain = website
            location_name = store["name"]
            street_address = store["address1"]
            city = store["city"]
            state = store["state"]
            zip = store["zipCode"]

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = store["storeID"]
            phone = store["phone"]

            location_type = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]

            hours_list = []
            try:
                hours = store["hourInfo"].split(";")
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        if (
                            "Thanksgiving" in "".join(hour).strip()
                            or "Christmas" in "".join(hour).strip()
                            or "Thaksgiving" in "".join(hour).strip()
                        ):
                            break
                        else:
                            hours_list.append("".join(hour).strip())
            except:
                pass

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace(
                    "Special hours for senior customers and customers needing extra assistance",
                    "",
                )
                .strip()
                .split(";;")[0]
                .strip()
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
