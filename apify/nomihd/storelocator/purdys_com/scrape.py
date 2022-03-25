# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "purdys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    locationtypes = ["1", "2"]

    for locationtype in locationtypes:

        api_url = f"https://www.purdys.com/Live/services/StoreLocator.Service.ss?c=4664544&locationtype={locationtype}&n=2&page=1&results_per_page=100&sort=namenohierarchy"
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)

        stores_list = json_res["records"]
        for store in stores_list:

            page_url = (
                f'https://www.purdys.com/shops/details/{store["internalid"].strip()}'
            )
            log.info(page_url)
            locator_domain = website
            location_name = store["name"].strip()

            street_address = store["address1"].strip()
            if (
                "address2" in street_address
                and store["address2"] is not None
                and len(store["address2"]) > 0
            ):
                street_address = street_address + ", " + store["address2"]

            city = store["city"].strip()
            state = store["state"].strip()
            zip = store["zip"].strip()

            country_code = store["country"].strip()

            store_number = store["internalid"].strip()
            phone = store["phone"].strip()

            location_type = "<MISSING>"
            if locationtype == "2":
                location_type = "Fulfillment"
                hours_of_operation = "<MISSING>"
            else:

                hours_html = store["custrecord_ssd_hours_of_operation"].strip()

                if "hours-time" in hours_html:

                    hours_sel = lxml.html.fromstring(
                        hours_html.replace("&lt;", "<")
                        .replace("&gt;", ">")
                        .replace('""', '"')
                        .strip()
                    )
                    hours_info = "".join(
                        hours_sel.xpath('//div[@class="hours-time"]/text()')
                    ).strip()
                    hours_info = (
                        hours_info.replace("pm ", "pm | ")
                        .replace("PM ", "PM | ")
                        .replace("closed ", "closed | ")
                        .replace("CLOSED", "CLOSED | ")
                    )
                    hours_info = hours_info.split(" | ")
                    temp_day_tags = hours_sel.xpath('//div[@class="hours-days"]/text()')
                    day_tags = []
                    for temp in temp_day_tags:
                        if len("".join(temp).strip()) > 0:
                            day_tags.append("".join(temp).strip())

                    hours_list = []

                    for idx, day in enumerate(day_tags, 0):
                        hours_list.append(f"{day}: {hours_info[idx]}")

                    hours_of_operation = "; ".join(hours_list)
                else:
                    hours_of_operation = "<MISSING>"

            latitude = store["location"]["latitude"]
            longitude = store["location"]["longitude"]
            raw_address = "<MISSING>"

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
