# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "veromoda.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.veromoda.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.veromoda.com/gb/en/stores",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.veromoda.com/gb/en/stores"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        countries = search_sel.xpath('//select[@id="country"]/option/@value')

        for country in countries:
            log.info(f"fetching stores for country:{country}")
            params = (
                ("countryCode", country),
                ("brandCode", "vm"),
            )

            cities_req = session.get(
                "https://www.veromoda.com/on/demandware.store/Sites-BSE-South-Site/en_GB/Stores-GetCities",
                headers=headers,
                params=params,
            )
            cities = cities_req.json()
            for cit in cities:
                params = (
                    ("countryCode", country),
                    ("brandCode", "vm"),
                    ("postalCodeCity", cit),
                    ("serviceID", "SDSStores"),
                    ("filterByClickNCollect", "false"),
                )
                stores_req = session.get(
                    "https://www.veromoda.com/on/demandware.store/Sites-BSE-South-Site/en_GB/PickupLocation-GetLocations",
                    headers=headers,
                    params=params,
                )
                stores = json.loads(stores_req.text)["locations"]
                for store in stores:

                    locator_domain = website
                    page_url = "<MISSING>"
                    location_name = store["storeName"]
                    location_type = store["brands"][0]["name"]

                    street_address = store["address1"]
                    city = store["city"]
                    state = "<MISSING>"
                    zip = store["postalCode"]
                    country_code = country

                    phone = store["phone"]
                    hours_of_operation = "<MISSING>"

                    store_number = store["storeID"]
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
