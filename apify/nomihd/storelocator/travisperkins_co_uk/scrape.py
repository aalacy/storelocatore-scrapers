# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "travisperkins.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.travisperkins.co.uk/branch-locator"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            stores_req.text.split("window.__PRELOADED_STATE__ = ")[1]
            .strip()
            .split("</script>")[0]
            .strip()
        )["branch"]["allBranches"]

        for store in stores:
            page_url = "https://www.travisperkins.co.uk/branch-locator/" + store["code"]

            locator_domain = website
            location_name = store["name"]
            street_address = store["address"]["line2"].strip()

            if (
                store["address"]["line3"] is not None
                and len(store["address"]["line3"]) > 0
            ):
                street_address = street_address + ", " + store["address"]["line3"]

            street_address = street_address.replace(
                "TRAVIS PERKINS TRADING CO. LTD,", ""
            ).strip()
            city = store["address"]["town"].strip()
            state = "<MISSING>"
            zip = store["address"]["postalCode"].strip()
            country_code = "GB"

            store_number = store["code"]
            phone = store["phone"].strip()

            location_type = "<MISSING>"

            latitude = str(store["geoPoint"]["lat"])
            longitude = str(store["geoPoint"]["lng"])

            hours = store["branchSchedule"]
            hours_list = []
            for hour in hours:
                day = hour["dayOfWeek"]
                if hour["closed"] is True:
                    time = "Closed"
                else:
                    time = hour["openingTime"] + "-" + hour["closingTime"]

                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
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
