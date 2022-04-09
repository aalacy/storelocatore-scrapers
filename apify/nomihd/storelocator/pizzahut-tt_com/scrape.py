# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut-tt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.pizzahut-tt.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.pizzahut-tt.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut-tt.com/en/store-locator.html"
    search_res = session.get(search_url, headers=headers)
    json_str = (
        search_res.text.split("window.pageData=")[1].strip().split("};")[0].strip()
        + "}"
    )
    stores = json.loads(json_str)["chainStores"]["msg"]
    for store in stores:
        locator_domain = website
        location_name = store["title"]["en_US"]
        page_url = (
            "https://www.pizzahut-tt.com/en/store-locator/"
            + location_name.replace(" ", "_").strip()
            + ".html"
        )

        street_address = (
            store["address"]["formatted"].replace(", Trinidad and Tobago", "").strip()
        )
        city = store["address"]["city"]
        if city:
            street_address = street_address.split(", " + city)[0].strip()
        state = "<MISSING>"
        zip = "<MISSING>"
        country_code = store["address"]["countryCode"]

        phone = store["contact"]["phone"]
        store_number = store["id"]

        location_type = "<MISSING>"

        hours_list = []
        try:
            hours = store["openingHours"][0]
            if "es" in hours:
                hours = hours["es"]
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
