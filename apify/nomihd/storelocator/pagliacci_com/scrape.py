# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pagliacci.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "cdn.contentful.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "application/json, text/plain, */*",
    "authorization": "Bearer UGZSG7eTBD5fwQaQvH1ow8aNaYX0_j64NbRWQCI8vpc",
    "sec-ch-ua-mobile": "?0",
    "x-contentful-user-agent": "sdk contentful.js/8.3.7; platform browser; os Windows;",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://pagliacci.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://pagliacci.com/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    api_url = "https://cdn.contentful.com/spaces/xlz6ggc5ewpj/environments/master/entries?content_type=location"
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)
        store_list = json_res["items"]
        for store in store_list:
            store = store["fields"]
            page_url = "https://pagliacci.com/locations/" + store["slug"].strip()

            locator_domain = website
            raw_address = store["address"].replace("\n", ", ").strip()

            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            location_name = store["name"].strip()

            phone = "(206) 726-1717"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_info = store["openHours"]["content"]
            hour_list = []
            for hour_info in hours_info:
                if "day" in hour_info["content"][0]["value"]:
                    hour_list.append(
                        f'{hour_info["content"][0]["value"].strip()}: {hour_info["content"][-1]["value"]}'
                    )
            hours_of_operation = "; ".join(hour_list)
            latitude, longitude = (
                store["location"]["lat"],
                store["location"]["lon"],
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
                raw_address=raw_address,
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
