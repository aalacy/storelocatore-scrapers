# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "edseasydiner.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here

    search_url = "https://edseasydiner.com/find-an-eds"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        json_str = (
            search_res.text.split(':restaurants="')[1]
            .split('"></find-controller>')[0]
            .strip()
            .replace("&quot;", '"')
        )

        stores = json.loads(json_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = store["yext_link"]

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = store["title"].strip()

            location_type = "<MISSING>"

            raw_address = "<MISSING>"
            lines = store["address_lines"]
            street_address = ", ".join([line["address_line"] for line in lines])

            city = store["city"]
            state = "<MISSING>"
            zip = store["post_code"]

            country_code = "GB"

            phone = store["telephone_number"]

            hours_sel = store_sel.xpath('//div[h3="Hours"]/div/ul')

            days = list(
                filter(str, [x.strip() for x in hours_sel[0].xpath(".//text()")])
            )

            hours = list(
                filter(str, [x.strip() for x in hours_sel[1].xpath(".//text()")])
            )
            hour_list = []
            for i, day in enumerate(days):
                hour_list.append(f"{day}: {hours[i]}")
            hours_of_operation = "; ".join(hour_list)

            store_number = store["id"]

            latitude, longitude = store["latitude"], store["longitude"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
