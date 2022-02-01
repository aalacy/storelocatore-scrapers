# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "crowndecoratingcentres.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "Pragma": "no-cache",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "If-Modified-Since": "Mon, 26 Jul 1997 05:00:00 GMT",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.crowndecoratingcentres.co.uk/stores",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (
    ("location", "null"),
    ("radius", "25"),
)


def fetch_data():
    # Your scraper here
    base = "https://www.crowndecoratingcentres.co.uk"
    api_url = "https://www.crowndecoratingcentres.co.uk/api/sitecore/crowndecorating/stores/search"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)

        json_res = json.loads(api_res.text)

        stores = json_res["Stockists"]

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = base + store["Url"]

            location_name = store["Name"].strip()

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = (
                (store["Address1"] + "," + store["Address2"]).strip().strip(", ")
            )

            city = store["City"]

            state = store["County"]

            zip = store["PostCode"]
            country_code = store["Country"]

            phone = store["Phone"]

            hours_info = store["StockistBusinessHours"]
            hour_list = []
            for hour_info in hours_info:
                opens = hour_info["OpenTime"]
                closes = hour_info["CloseTime"]

                day = hour_info["DayOfWeek"]

                if opens != closes:

                    hour_list.append(f"{day}: {opens}-{closes}")
                else:
                    hour_list.append(f"{day}: Closed")

            hours_of_operation = (
                "; ".join(hour_list).replace(":;", ":").replace("day;", "day:")
            )
            store_number = store["StoreCode"]

            latitude, longitude = store["Latitude"], store["Longitude"]
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
