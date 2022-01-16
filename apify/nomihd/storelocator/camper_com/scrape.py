# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "camper.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.camper.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    countires = [
        "https://camper.com/en_US/shops/usa",
        "https://camper.com/en_US/shops/ca",
        "https://camper.com/en_US/shops/uk",
    ]
    base = "https://www.camper.com/en_US/shops"
    with SgRequests(proxy_country="us", dont_retry_status_codes=([404])) as session:
        for country_url in countires:

            api_url = country_url
            api_res = session.get(api_url, headers=headers)
            json_str = (
                api_res.text.split('__NEXT_DATA__" type="application/json">')[1]
                .split("</script>")[0]
                .strip()
            )
            json_res = json.loads(json_str)

            store_list = json_res["props"]["pageProps"]["preloadedStores"]

            for store in store_list:

                page_url = base + store["url"]
                locator_domain = website

                street_address = store["address1"]
                city = store["cityName"]
                state = store.get("region", "<MISSING>")
                if state.isdigit():
                    state = "<MISSING>"

                zip = store["postalCode"]

                country_code = store["countryCode"]

                location_name = store["name"]

                phone = store["telephone"]

                store_number = store["id"]

                location_type = "<MISSING>"
                hours = store["storeHours"]
                hour_list = []
                for hour in hours:
                    hour_list.append(f"{hour['days']}: {hour['timetable']}")

                hours_of_operation = "; ".join(hour_list).replace(":;", ":").strip()

                latitude, longitude = (
                    store["latitude"],
                    store["longitude"],
                )
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
