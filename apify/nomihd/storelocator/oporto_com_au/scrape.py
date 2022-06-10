# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "oporto.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.oporto.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.oporto.com.au/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.oporto.com.au/locations/"
    api_url = "https://www.oporto.com.au/api/stores/2/"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)
        stores = json_res

        for store in stores:

            locator_domain = website

            location_name = store["title"]
            page_url = search_url + store["slug"]

            location_type = "<MISSING>"
            raw_address = "<MISSING>"
            street_address = store["address"]
            if street_address and street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            city = store["suburb"]
            state = store["state"]
            zip = store["postcode"]

            country_code = "AU"

            phone = store["phone"]

            hours = store["opening_hours"]
            hour_list = []
            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]:
                if not isinstance(hours[day], bool):
                    opening = hours[day]["open"]
                    closing = hours[day]["close"]
                    hour_list.append(f"{day}: {opening} - {closing}")
                else:
                    hour_list.append(f"{day}: Closed")

            hours_of_operation = "; ".join(hour_list)
            store_number = store["id"]

            latitude, longitude = store["latitude"], store["longitude"]

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
