# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "kolachefactory.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "liveapi.yext.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://locations.kolachefactory.com",
    "referer": "https://locations.kolachefactory.com/",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    for x in range(0, 200, 50):
        api_url = f"https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location=%2210001%22&offset={x}&limit=50&api_key=5038bd284b1a928be269472fd2a84e8a&v=20181201&resolvePlaceholders=true&entityTypes=restaurant"

        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)

        store_list = json_res["response"]["entities"]

        if not store_list:
            break

        for store in store_list:

            store_number = store["meta"]["id"]
            page_url = store.get("landingPageUrl", "")

            locator_domain = website

            location_name = store.get("name", "Kolache Factory")
            if "coming soon" in location_name.lower():
                continue
            street_address = store["address"]["line1"].strip()
            if "line2" in store and store["address"]:
                street_address = (
                    street_address + ", " + store["address"]["line2"]
                ).strip(", .")

            city = store["address"]["city"].strip()
            state = store["address"]["region"].strip()

            zip = store["address"]["postalCode"].strip()

            country_code = store["address"]["countryCode"].strip()
            phone = store["mainPhone"]

            location_type = "<MISSING>"
            hours = store.get("hours", "")
            hour_list = []
            if hours:
                for day in [
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ]:
                    if day in hours:
                        if hours[day].get("openIntervals"):
                            hour_list.append(
                                f"{day}: {hours[day]['openIntervals'][0]['start']} - {hours[day]['openIntervals'][0]['end']}"
                            )
                        else:
                            hour_list.append(f"{day}: Closed")
                    else:
                        hour_list.append(f"{day}: Closed")

            hours_of_operation = "; ".join(hour_list)

            if "closed" in location_name.lower():
                location_type = "Permanently Closed"
                hours_of_operation = "<MISSING>"

            latitude = store["yextDisplayCoordinate"]["latitude"]
            longitude = store["yextDisplayCoordinate"]["longitude"]

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
