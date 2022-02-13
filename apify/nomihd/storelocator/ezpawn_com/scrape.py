# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "ezpawn.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here

    with SgRequests() as session:
        stores_req = session.get(
            "https://ezpawn.com/data/locations/ezpawn/output/locations.json",
            headers=headers,
        )
        stores = json.loads(stores_req.text)
        for store in stores:

            locator_domain = website
            location_name = store["name2"]
            street_address = store["address"]
            city = store["city"].replace(" ", "-").strip()
            state = store["state"]
            zip = store["zip"]
            country_code = store["countryCode"]
            store_number = "<MISSING>"
            phone = store["phone"]
            location_type = store["name"]

            latitude = store["latitude"]
            longitude = store["longitude"]
            page_url = store["url"]
            log.info(page_url)
            hours_list = []
            try:
                store_req = SgRequests.raise_on_err(
                    session.get(page_url, headers=headers)
                )
                store_sel = lxml.html.fromstring(store_req.text)
                days = store_sel.xpath('//dl[@class="sched-box"]/dt')
                time = store_sel.xpath('//dl[@class="sched-box"]/dd')
                for index in range(0, len(days)):
                    day = "".join(days[index].xpath(".//text()")).strip()
                    tim = "".join(time[index].xpath(".//text()")).strip()
                    hours_list.append(day + ":" + tim)

            except SgRequestError as e:
                log.error(e.status_code)

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
