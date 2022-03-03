# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "olgas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "order.olgas.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "x-olo-viewport": "Desktop",
    "x-olo-country": "us",
    "x-olo-request": "1",
    "x-olo-app-platform": "web",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "application/json, */*",
    "sec-ch-ua-mobile": "?0",
    "x-requested-with": "XMLHttpRequest",
    "__requestverificationtoken": "",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://order.olgas.com/locations",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("excludeCities", "true"),)


def fetch_data():
    # Your scraper here

    search_url = "https://order.olgas.com/api/vendors/regions"
    states_req = session.get(search_url, headers=headers, params=params)
    states = json.loads(states_req.text)
    for st in states:
        code = st["code"]
        stores_API_URL = f"https://order.olgas.com/api/vendors/search/{code}"
        stores_req = session.get(stores_API_URL, headers=headers)
        stores = json.loads(stores_req.text)["vendor-search-results"]
        for store in stores:
            page_url = "http://order.olgas.com/menu/" + store["slug"]
            locator_domain = website
            location_name = store["name"].replace("&#8211;", "-").strip()

            street_address = store["address"]["streetAddress"]
            if (
                store["address"]["streetAddress2"] is not None
                and len(store["address"]["streetAddress2"]) > 0
            ):
                street_address = (
                    street_address + ", " + store["address"]["streetAddress2"]
                )

            street_address = street_address.replace("Breeze Dining Court,", "").strip()
            if "Online Only" in street_address:
                continue

            city = store["address"]["city"]
            state = store["address"]["state"]
            zip = store["address"]["postalCode"]

            country_code = store["address"]["country"]

            store_number = store["id"]
            phone = store["phoneNumber"]

            location_type = "<MISSING>"
            hours_list = []
            hours_type = store["weeklySchedule"]["calendars"]
            for typ in hours_type:
                if typ["scheduleDescription"] == "Business":
                    hours = typ["schedule"]
                    for hour in hours:
                        day = hour["weekDay"]
                        time = hour["description"]
                        hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["latitude"]
            longitude = store["longitude"]

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
