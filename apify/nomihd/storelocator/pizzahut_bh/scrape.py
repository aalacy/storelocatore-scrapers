# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.bh"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Referer": "https://www.pizzahut.bh/",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    params = (
        ("l", "en"),
        ("isFullData", "1"),
    )

    search_res = session.get(
        "https://www.pizzahut.bh/Handlers/ItemsInfo.ashx",
        headers=headers,
        params=params,
    )
    stores = json.loads(
        search_res.text.split("var OriginalStores=")[1].strip().split(";var")[0].strip()
    )

    for key in stores.keys():
        store_number = stores[key]["ID"]
        page_url = f"https://www.pizzahut.bh/#/store/{store_number}"
        locator_domain = website
        location_name = stores[key]["Name"]
        if location_name == "PH Web Store":
            continue
        raw_address = stores[key]["Address"].split(",")
        street_address = "<MISSING>"
        city = "<MISSING>"
        if len(raw_address) > 1:
            street_address = ", ".join(raw_address[:-1]).strip()
            city = raw_address[-1]
            if city == "Bahrain":
                city = "<MISSING>"
        else:
            street_address = ", ".join(raw_address).strip()

        state = "<MISSING>"
        zip = "<MISSING>"

        country_code = "BH"
        phone = "<MISSING>"

        location_type = "<MISSING>"

        hours_list = []
        hours_list.append(
            "Saturday: "
            + stores[key]["SaturdayDeliveryStart"]
            + " - "
            + stores[key]["SaturdayDeliveryEnd"]
        )
        hours_list.append(
            "Sunday: "
            + stores[key]["SundayDeliveryStart"]
            + " - "
            + stores[key]["SundayDeliveryEnd"]
        )
        hours_list.append(
            "Monday: "
            + stores[key]["MondayDeliveryStart"]
            + " - "
            + stores[key]["MondayDeliveryEnd"]
        )
        hours_list.append(
            "Tuesday: "
            + stores[key]["TuesdayDeliveryStart"]
            + " - "
            + stores[key]["TuesdayDeliveryEnd"]
        )
        hours_list.append(
            "Wednesday: "
            + stores[key]["WednesdayDeliveryStart"]
            + " - "
            + stores[key]["WednesdayDeliveryEnd"]
        )
        hours_list.append(
            "Thursday: "
            + stores[key]["ThursdayDeliveryStart"]
            + " - "
            + stores[key]["ThursdayDeliveryEnd"]
        )
        hours_list.append(
            "Friday: "
            + stores[key]["FridayDeliveryStart"]
            + " - "
            + stores[key]["FridayDeliveryEnd"]
        )

        hours_of_operation = (
            "; ".join(hours_list).strip().replace("26:45", "02:45").strip()
        )

        latitude, longitude = (
            stores[key]["MapLocation"]["Latitude"],
            stores[key]["MapLocation"]["Longitude"],
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
