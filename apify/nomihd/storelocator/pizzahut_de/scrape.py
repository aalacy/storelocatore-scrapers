# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "fb-eu.tictuk.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://pizzahut.de",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://pizzahut.de/de/store-locator.json"
    with SgRequests() as session:

        stores_req = session.get(
            search_url,
            headers=headers,
        )

        stores = json.loads(stores_req.text)["chainStores"]["msg"]
        for store in stores:
            location_name = store["title"]["de_DE"]
            page_url = (
                "https://pizzahut.de/de/store-locator/"
                + location_name.replace(" ", "_").strip()
            )
            location_type = "<MISSING>"
            locator_domain = website

            raw_address = (
                store["address"]["formatted"]
                .strip()
                .replace(", Deutschland", "")
                .strip()
            )
            street_address = raw_address.split(",")[0].strip()
            city = state = zip = "<MISSING>"

            if len(raw_address.split(",")) > 1:
                city = raw_address.split(",")[-1].strip().split(" ", 1)[-1].strip()
                zip = raw_address.split(",")[-1].strip().split(" ")[0].strip()

            country_code = store["address"]["countryCode"]
            store_number = store["id"]
            phone = store["contact"]["phone"]
            hours_list = []
            try:
                hours = store["openingHours"][0]
                if "de" in hours:
                    hours = hours["de"]
                elif "en" in hours:
                    hours = hours["en"]
                for index in range(0, len(hours)):
                    if index == 0:
                        day = "Sun"
                    if index == 1:
                        day = "Mon"
                    if index == 2:
                        day = "Tue"
                    if index == 3:
                        day = "Wed"
                    if index == 4:
                        day = "Thu"
                    if index == 5:
                        day = "Fri"
                    if index == 6:
                        day = "Sat"

                    tim = hours[index][0]

                    hours_list.append(day + ": " + tim)
            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["address"]["latLng"]["lat"]
            longitude = store["address"]["latLng"]["lng"]

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
