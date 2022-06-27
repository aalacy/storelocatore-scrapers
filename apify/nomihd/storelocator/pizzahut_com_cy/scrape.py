# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.com.cy"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut.com.cy",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.pizzahut.com.cy/restaurants/delivery",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    params = (
        ("api", "phc"),
        ("method", "getDistricts"),
    )

    search_res = session.get(
        "https://www.pizzahut.com.cy/", headers=headers, params=params
    )

    cities = json.loads(search_res.text)["data"]

    for city in cities:
        cityid = city["cityid"]
        state = city["cityname"]
        stores_req = session.get(
            f"https://www.pizzahut.com.cy/?api=phc&method=getShopsByDistrictId&districtId={cityid}",
            headers=headers,
        )
        stores = json.loads(stores_req.text)["data"]
        for store in stores:
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["name_en"]
            raw_address = store["info_en"].split(",")
            street_address = ", ".join(raw_address[:-1]).strip()
            city = raw_address[-1].strip().rsplit(" ", 1)[0].strip()
            zip = raw_address[-1].strip().rsplit(" ", 1)[-1].strip()

            if location_name == "PHINIKOUDES":
                street_address = "Larnaca seafront"
                city = "<MISSING>"
                zip = "<MISSING>"

            if zip.isdigit() is False:
                zip = "<MISSING>"
                city = "<MISSING>"

            country_code = "CY"
            phone = "<MISSING>"

            try:
                phone = store["phone"]
            except:
                pass

            store_number = store["lid"]

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            try:
                hours_of_operation = (
                    store["scheduleData"]["data"]["schedule"]["opened"]
                    + " - "
                    + store["scheduleData"]["data"]["schedule"]["closed"]
                )
            except:
                pass
            latitude, longitude = (
                store["coordinates"].split(",")[0].strip(),
                store["coordinates"].split(",")[-1].strip(),
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
