# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.dynamic import DynamicGeoSearch
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "longchamp.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.longchamp.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_records_for(tup):
    coords, CurrentCountry, countriesRemaining, session = tup
    lat = coords[0]
    lng = coords[1]
    log.info(
        f"pulling records for Country-{CurrentCountry} Country#:{countriesRemaining},\n coordinates: {lat,lng}"
    )
    search_url = "https://www.longchamp.com/on/demandware.store/Sites-Longchamp-EU-Site/en/Stores-FindStores"
    params = (
        ("showMap", "true"),
        ("findInStore", "false"),
        ("productId", "false"),
        ("checkboxStore", "stock"),
        ("radius", "300"),
        ("lat", lat),
        ("lng", lng),
        ("entityType", "Place"),
        ("entitySubType", ""),
        ("countryRegion", ""),
        ("formattedSuggestion", ""),
    )
    stores = []
    try:
        stores_req = SgRequests.raise_on_err(session.get(search_url, params=params))
        stores = json.loads(stores_req.text)["stores"]
    except SgRequestError as e:
        log.info("Error Code: " + e.status_code)

    return stores, CurrentCountry


def process_record(raw_results_from_one_coordinate):
    stores, current_country = raw_results_from_one_coordinate
    for store in stores:
        if store["type"] != "BTQ":
            continue
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["name"]
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store.get("city", "<MISSING>")
        state = store.get("stateCode", "<MISSING>")
        zip = store.get("postalCode", "<MISSING>")
        country_code = store["countryCode"]
        if country_code == "" or country_code is None:
            country_code = current_country

        store_number = store["ID"]
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"
        hours_list = []
        hours = store.get("storeHours", [])
        days_dict = {
            "1": "Sunday",
            "2": "Monday",
            "3": "Tuesday",
            "4": "Wednesday",
            "5": "Thursday",
            "6": "Friday",
            "7": "Saturday",
        }
        for hour in hours:
            day = days_dict.get(hour["day"])
            time = hour["openingTime"] + "-" + hour["closingtime"]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
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
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as session:
            session.get(
                "https://www.longchamp.com/en/en/stores?showMap=true", headers=headers
            )

            countries = (
                SearchableCountries.WITH_ZIPCODE_AND_COORDS
                + SearchableCountries.WITH_COORDS_ONLY
            )
            totalCountries = len(countries)
            currentCountryCount = 0
            for country in countries:
                try:
                    search = DynamicGeoSearch(
                        expected_search_radius_miles=50, country_codes=[country]
                    )
                    results = parallelize(
                        search_space=[
                            (
                                coord,
                                search.current_country(),
                                str(f"{currentCountryCount}/{totalCountries}"),
                                session,
                            )
                            for coord in search
                        ],
                        fetch_results_for_rec=fetch_records_for,
                        processing_function=process_record,
                    )
                    for rec in results:
                        writer.write_row(rec)
                        count = count + 1
                    currentCountryCount += 1
                except Exception as e:
                    log.error(f"{country}: not found\n{e}")
                    currentCountryCount += 1
                    pass

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
