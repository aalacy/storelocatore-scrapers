# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hurricanewings.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "api.momentfeed.com",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    url = (
        "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token"
        "=VZWYVLJIAZZFRMHS&multi_account=false&page={}&pageSize=100"
    )
    page_no = 1
    while True:
        stores_req = session.get(
            url.format(str(page_no)),
            headers=headers,
        )
        stores = json.loads(stores_req.text)
        if "message" in stores:
            if stores["message"] == "No matching locations found":
                break

        for store in stores:
            locator_domain = website
            location_name = store["store_info"]["name"]
            street_address = store["store_info"]["address"]
            if len(store["store_info"]["address_extended"]) > 0:
                street_address = (
                    street_address + ", " + store["store_info"]["address_extended"]
                )
            city = store["store_info"]["locality"]
            state = store["store_info"]["region"]
            zip = store["store_info"]["postcode"]
            country_code = store["store_info"]["country"]
            page_url = "https://locations.hurricanewings.com" + store["llp_url"]
            phone = store["store_info"]["phone"]
            store_number = "<MISSING>"

            location_type = store["store_info"]["status"]
            latitude = store["store_info"]["latitude"]
            longitude = store["store_info"]["longitude"]
            hours = store["store_info"]["store_hours"]
            hours_list = []
            if len(hours) > 0:
                hours = hours.split(";")
                for index in range(0, len(hours) - 1):
                    day_val = hours[index].split(",")[0].strip()
                    day = ""
                    if day_val == "1":
                        day = "Monday:"
                    if day_val == "2":
                        day = "Tuesday:"
                    if day_val == "3":
                        day = "Wednesday:"
                    if day_val == "4":
                        day = "Thursday:"
                    if day_val == "5":
                        day = "Friday:"
                    if day_val == "6":
                        day = "Saturday:"
                    if day_val == "7":
                        day = "Sunday:"

                    time = hours[index].split(",", 1)[1].replace(",", " - ").strip()
                    try:
                        time = (
                            time.split("-")[0].strip()[:2]
                            + ":"
                            + time.split("-")[0].strip()[2:]
                            + " - "
                            + time.split("-")[-1].strip()[:2]
                            + ":"
                            + time.split("-")[-1].strip()[2:]
                        )
                    except:
                        pass
                    hours_list.append(day + time)

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

        page_no = page_no + 1


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
