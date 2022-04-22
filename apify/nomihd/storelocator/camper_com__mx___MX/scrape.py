# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
import json

website = "camper.com/mx_MX"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.camper.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:

        countries = SearchableCountries.ALL
        for country in countries:
            if country == "us" or country == "ca" or country == "gb":
                continue

            log.info(f"pulling records for country: {country}")
            params = (
                ("profile", "mx_MX"),
                ("countryCode", country),
            )

            search_res = session.get(
                "https://www.camper.com/eshop-api/api/v1/store-locator/stores",
                headers=headers,
                params=params,
            )
            stores = json.loads(search_res.text)["stores"]

            for store in stores:

                page_url = store.get("url", "<MISSING>")
                if page_url:
                    page_url = "https://www.camper.com/mx_MX/shops" + page_url
                locator_domain = website

                location_name = store.get("name", "<MISSING>")

                street_address = store.get("address1", "<MISSING>")
                city = store.get("cityName", "<MISSING>")
                state = "<MISSING>"
                zip = store.get("postalCode", "<MISSING>")

                country_code = store["countryCode"]

                store_number = store["id"]
                phone = store.get("telephone", "<MISSING>")
                hours_list = []
                try:
                    hours = store["storeHours"]
                    for hour in hours:
                        day = hour["days"]
                        time = hour["timetable"]
                        hours_list.append(day + ": " + time)
                except:
                    pass

                hours_of_operation = "; ".join(hours_list).strip()

                location_type = store["status"]
                latitude, longitude = store["latitude"], store["longitude"]

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
