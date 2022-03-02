# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "beaconlighting.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.beaconlighting.com.au",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("sections", "amasty-storepickup-data"),
    ("force_new_section_timestamp", "false"),
)


def fetch_data():
    # Your scraper here
    search_url = "https://www.beaconlighting.com.au/customer/section/load/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers, params=params)
        stores = json.loads(stores_req.text)["amasty-storepickup-data"]["stores"][
            "items"
        ]

        for store in stores:
            store_number = store["branch_code"]
            slug = store["url_key"]
            page_url = f"https://www.beaconlighting.com.au/storelocator/{slug}"
            locator_domain = website
            location_name = store["name"]

            street_address = store["address"]
            city = store["city"]
            state = store["region"]["region_code"]
            zip = store["zip"]

            country_code = store["country"]
            phone = store.get("phone", "<MISSING>")

            location_type = "<MISSING>"
            if store["franchise_store"] == "1":
                location_type = "franchise_store"

            latitude = store["lat"]
            longitude = store["lng"]

            hours_of_operation = "<MISSING>"
            if "schedule_string" in store:
                hours = json.loads(store["schedule_string"].replace('\\"', '"').strip())
                hours_list = []
                for day in hours.keys():
                    current_day = hours[day]
                    for st in current_day.keys():
                        if "_status" in st:
                            if hours[day][st] == "0":
                                time = "Closed"
                            else:
                                time = (
                                    hours[day]["from"]["hours"]
                                    + ":"
                                    + hours[day]["from"]["minutes"]
                                    + " - "
                                    + hours[day]["to"]["hours"]
                                    + ":"
                                    + hours[day]["to"]["minutes"]
                                )
                            break

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
