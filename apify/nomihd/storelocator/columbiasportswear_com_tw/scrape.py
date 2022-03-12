# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "columbiasportswear.com.tw"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "webapi.91app.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "origin": "https://www.columbiasportswear.com.tw",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.columbiasportswear.com.tw/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.columbiasportswear.com.tw/v2/Shop/StoreList/38253"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        params = (
            ("lat", "25.037929"),
            ("lon", "121.548818"),
            ("startIndex", "0"),
            ("maxCount", "100"),
            ("r", "null"),
            ("isEnableRetailStore", "false"),
            ("lang", "zh-TW"),
            ("shopId", "38253"),
        )

        search_res = session.get(
            "https://webapi.91app.com/webapi/LocationV2/GetLocationList",
            headers=headers,
            params=params,
        )

        stores = json.loads(search_res.text)["Data"]["List"]

        for store in stores:

            page_url = search_url

            locator_domain = website

            location_name = store["Name"]

            street_address = store["Address"]

            city = store["CityName"]
            state = "<MISSING>"
            zip = store["ZipCode"]

            country_code = "TW"

            store_number = store["OuterLocationCode"]

            phone = "<MISSING>"
            if len(store["Tel"]) > 0:
                phone = "(" + store["TelPrepend"] + ") " + store["Tel"]

            location_type = "<MISSING>"
            hours_of_operation = store["NormalTime"]
            latitude, longitude = (
                store["Latitude"],
                store["Longitude"],
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
