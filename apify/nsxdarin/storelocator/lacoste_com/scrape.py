# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "lacoste.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://global.lacoste.com/en/stores"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        region_str = (
            search_res.text.split('"searchList":')[1].split(',"store":')[0].strip()
        )

        region_list = json.loads(region_str)

        for region in region_list:

            region_url = search_url + region["url"]
            log.info(region_url)

            region_res = session.get(region_url, headers=headers)
            try:
                country_str = (
                    region_res.text.split('"searchList":')[1]
                    .split(',"store":')[0]
                    .strip()
                )
            except:
                continue

            country_list = json.loads(country_str)

            for countryy in country_list:  # countryy is json

                country_url = search_url + countryy["url"]
                log.info(country_url)
                country_res = session.get(country_url, headers=headers)
                try:
                    cities_str = (
                        country_res.text.split('"searchList":')[1]
                        .split(',"store":')[0]
                        .strip()
                    )
                except:
                    continue

                cities = json.loads(cities_str)
                for cityy in cities:  # cityy is json

                    api_url = (
                        search_url
                        + f'?country={cityy["url"].split("/")[1]}&city={cityy["url"].split("/")[-1]}&json=true'
                    )
                    log.info(api_url)

                    if "=null" in api_url:
                        continue

                    api_res = session.get(api_url, headers=headers)
                    json_res = json.loads(api_res.text)

                    stores = json_res["stores"]

                    for idx, store in enumerate(stores, 1):

                        locator_domain = website

                        location_name = store["name"].strip()

                        page_url = search_url + store["url"]

                        raw_address = "<MISSING>"

                        street_address = store["address"]
                        if street_address:
                            street_address = (
                                street_address.replace("&#35;", "#")
                                .strip()
                                .replace("&#41;", ")")
                                .strip()
                                .replace("&#40;", "(")
                                .strip()
                                .replace("&#39;", "'")
                                .strip()
                            )

                        city = store["city"]
                        state = store.get("state")
                        zip = store["postalCode"]
                        if zip:
                            zip = zip.strip(":* ")

                        country_code = json_res["country"]
                        phone = store["phone"]

                        if phone and phone.strip("+ ").strip() == "":
                            phone = "<MISSING>"

                        location_type = store["type"]

                        store_number = store["id"]
                        hours = store["hours"]
                        if hours:

                            hours_of_operation = (
                                hours.replace("1-6", "Mon-Sat: ")
                                .replace("1-4", "Mon-Thu: ")
                                .replace("5-6", "Fri-Sat: ")
                                .replace("7:", "Sun: ")
                                .replace(",", "; ")
                                .replace("1-Sun", "Mon-Sun")
                                .replace(": :", ":")
                                .replace("6-Sun", "Sat-Sun")
                                .replace("6:", "Sat:")
                            )
                        else:
                            hours_of_operation = "<MISSING>"

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
