# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.simple_utils import parallelize
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

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


def fetch_records_for(tup):
    coords, CurrentCountry, countriesRemaining = tup
    lat = coords[0]
    lng = coords[1]
    log.info(
        f"pulling info for country: {CurrentCountry} having coordinates as {lat},{lng}"
    )

    search_url = "https://www.thomassabo.com/on/demandware.store/Sites-TS_INT-Site/en/Shopfinder-GetStores?searchMode=radius&searchPhrase={}&searchDistance={}&lat={}&lng={}&filterBy="

    stores_req = session.get(search_url.format("", 100000, lat, lng), headers=headers)
    stores = []

    try:
        stores = json.loads(stores_req.text)
    except:
        pass

    return stores


def process_record(raw_results_from_one_coordinate):
    stores = raw_results_from_one_coordinate
    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store.get("name", "<MISSING>")
        if "address1" in store:
            street_address = store["address1"]
            if (
                "address2" in store
                and store["address2"] is not None
                and len(store["address2"]) > 0
            ):
                street_address = street_address + ", " + store["address2"]
        else:
            if "address2" in store:
                street_address = store["address2"]

        city = store.get("city", "<MISSING>")
        state = store.get("stateCode", "<MISSING>")
        zip = store.get("postalCode", "<MISSING>")
        country_code = store.get("countryCode", "<MISSING>")
        store_number = store["ID"]
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"
        try:
            location_type = store["category"]["displayValue"]
        except:
            pass
        hours_of_operation = ""
        try:
            hours = BeautifulSoup(store["storeHours"], "lxml")
            list_hours = list(hours.stripped_strings)
            hours_of_operation = " ".join(list_hours).strip().replace("\n", " ").strip()
        except:
            pass

        latitude = store.get("latitude", "<MISSING>")
        try:
            latitude = str(latitude)
        except:
            pass
        longitude = store.get("longitude", "<MISSING>")
        try:
            longitude = str(longitude)
        except:
            pass

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
        countries = SearchableCountries.ALL
        totalCountries = len(countries)
        currentCountryCount = 0
        for country in countries:
            try:
                search = DynamicGeoSearch(
                    expected_search_radius_miles=100, country_codes=[country.upper()]
                )
                results = parallelize(
                    search_space=[
                        (
                            coord,
                            country.upper(),
                            str(f"{currentCountryCount}/{totalCountries}"),
                        )
                        for coord in search
                    ],
                    fetch_results_for_rec=fetch_records_for,
                    processing_function=process_record,
                    max_threads=20,  # tweak to see what's fastest
                )
                for rec in results:
                    writer.write_row(rec)
                currentCountryCount += 1
            except Exception as e:
                log.error(f"{country}: not found\n{e}")
                currentCountryCount += 1
                pass

    log.info("Finished")


if __name__ == "__main__":
    scrape()
