# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "eatatelmers.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "eatatelmers.com",
    "accept": "*/*",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "referer": "https://eatatelmers.com/locations/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

params = {
    "filter": '{"map_id":"1","mashupIDs":[],"customFields":[]}',
}


def fetch_data():
    # Your scraper here

    with SgRequests() as session:
        search_res = session.get(
            "https://eatatelmers.com/wp-json/wpgmza/v1/features/",
            headers=headers,
            params=params,
        )

        stores = json.loads(search_res.text)["markers"]

        for store in stores:
            page_url = "https://eatatelmers.com/locations/"
            store_sel = lxml.html.fromstring(store["description"])

            locator_domain = website

            location_name = store["title"]

            raw_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath('//div[@class="address"]/text()')
                    ],
                )
            )

            if "USA" in ",".join(raw_info):
                raw_address = store["address"].split(",")
                street_address = ", ".join(raw_address[:-2]).strip()
                city = raw_address[-2].strip()
                state = raw_address[-1].strip().split(" ")[0].strip()
                zip = raw_address[-1].strip().split(" ")[-1].strip()

            else:
                street_address = ", ".join(raw_info[:-2]).strip()
                city = raw_info[-2].strip().split(",")[0].strip()
                state = (
                    raw_info[-2].strip().split(",")[-1].strip().split(" ")[0].strip()
                )
                zip = raw_info[-2].strip().split(",")[-1].strip().split(" ")[-1].strip()

            country_code = "US"

            phone = raw_info[-1].strip()
            store_number = store["id"]

            location_type = "<MISSING>"

            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="directions-hours"]/text()')
            ).strip()

            latitude = store["lat"]
            longitude = store["lng"]

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
