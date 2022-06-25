# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sumosalad.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "sumosalad.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://sumosalad.com/locate-your-nearest-store/"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        json_str = (
            search_res.text.split("var stores_list =")[1].split("];")[0].strip()
        ) + "]"

        json_str = (
            json_str.replace("name", '"name"')
            .replace("lat", '"lat"')
            .replace("lng", '"lng"')
            .replace("address", '"address"')
            .replace("country", '"country"')
            .replace("state", '"state"')
            .replace("suburb", '"suburb"')
            .replace("zip", '"zip"')
            .replace("phone", '"phone"')
            .replace("monday_hours", '"monday_hours"')
            .replace("tuesday_hours", '"tuesday_hours"')
            .replace("wednesday_hours", '"wednesday_hours"')
            .replace("thursday_hours", '"thursday_hours"')
            .replace("friday_hours", '"friday_hours"')
            .replace("saturday_hours", '"saturday_hours"')
            .replace("sunday_hours", '"sunday_hours"')
        )

        stores = json.loads(json_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url

            location_name = store["name"]
            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = store["address"]

            city = store["suburb"]

            state = store["state"]

            zip = store["zip"]

            country_code = "AU"

            phone = store["phone"]

            hours = []

            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]:
                time = store[f"{day}_hours"]
                if len(time) > 0:
                    hours.append(f"{day}: {time}")

            hours_of_operation = "; ".join(hours)

            store_number = "<MISSING>"

            latitude, longitude = store["lat"], store["lng"]
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
