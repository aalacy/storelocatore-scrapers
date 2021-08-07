# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thomassabo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.thomassabo.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.thomassabo.com/INT/en/shopfinder",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    data = session.get(
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"
    ).json()

    for feature in data["features"]:
        coordinates = feature["geometry"]["coordinates"][0][0]
        country = feature["properties"]["ISO_A2"]
        search_url = "https://www.thomassabo.com/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=country&searchPhrase={}&searchDistance={}&lat={}&lng={}&filterBy="
        for coord in coordinates:
            lat = coord[1]
            lng = coord[0]
            log.info(
                f"pulling info for country: {country} having coordinates as {lat},{lng}"
            )

            stores_req = session.get(
                search_url.format(country, 75, lat, lng), headers=headers
            )
            stores = json.loads(stores_req.text)
            for store in stores:
                page_url = "<MISSING>"
                locator_domain = website
                location_name = store["name"]
                street_address = store["address1"]
                if (
                    "address2" in store
                    and store["address2"] is not None
                    and len(store["address2"]) > 0
                ):
                    street_address = street_address + ", " + store["address2"]

                city = store.get("city", "<MISSING>")
                state = store.get("stateCode", "<MISSING>")
                zip = store.get("postalCode", "<MISSING>")
                country_code = store["countryCode"]
                store_number = store["ID"]
                phone = store.get("phone", "<MISSING>")

                location_type = store["category"]["displayValue"]
                hours_of_operation = ""
                try:
                    hours = BeautifulSoup(store["storeHours"], "lxml")
                    list_hours = list(hours.stripped_strings)
                    hours_of_operation = " ".join(list_hours).strip()
                except:
                    pass

                latitude = store["latitude"]
                longitude = store["longitude"]

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
