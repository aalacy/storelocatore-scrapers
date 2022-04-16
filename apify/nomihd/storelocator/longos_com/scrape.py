# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "longos.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.longos.com/locations/"
    api_url = "https://api.longos.com/ggcommercewebservices/v2/groceryGatewaySpa/stores?fields=stores(displayName,name,address(FULL),%20%20%20%20%20%20openingHours(FULL),geoPoint(FULL),holidayHours(FULL))&lang=en&curr=CAD&pageSize=100"

    with SgRequests(proxy_country="us", dont_retry_status_codes=([404])) as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)
        stores = json_res["stores"]

        for store in stores:

            page_url = search_url

            location_name = store["displayName"]
            location_type = "<MISSING>"
            store_info = store["address"]

            locator_domain = website

            street_address = store_info["line1"].strip()
            if store_info.get("line2"):
                street_address = (store_info["line2"] + " " + street_address).strip()

            city = store_info["town"]

            if store_info.get("region"):
                state = store_info["region"]["isocodeShort"]
            else:
                state = "<MISSING>"
            zip = store_info["postalCode"]

            country_code = store_info["country"]["isocode"]

            store_number = store_info["id"]

            phone = store_info["phone"]

            hours_info = store["openingHours"]["weekDayOpeningList"]

            hour_list = []
            for hour in hours_info:
                if hour.get("closed"):
                    hour_list.append(f"{hour['weekDay']}: Closed")
                else:
                    hour_list.append(
                        f"{hour['weekDay']}: {hour['openingTime']['formattedHour']} - {hour['closingTime']['formattedHour']}"
                    )

            hours_of_operation = "; ".join(hour_list).replace("day; ", "day: ").strip()

            latitude, longitude = (
                store["geoPoint"]["latitude"],
                store["geoPoint"]["longitude"],
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
