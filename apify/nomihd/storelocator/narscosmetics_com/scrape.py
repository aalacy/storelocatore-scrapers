# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.dynamic import DynamicGeoSearch
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "narscosmetics.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://hosted.where2getit.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://hosted.where2getit.com/narscosmetics/index2017.html?null&search=Go",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


id_list = []


def fetch_records_for(tup):
    coords, CurrentCountry, countriesRemaining = tup
    lat = coords[0]
    lng = coords[1]
    log.info(
        f"pulling records for Country-{CurrentCountry} Country#:{countriesRemaining},\n coordinates: {lat,lng}"
    )
    search_url = "https://hosted.where2getit.com/narscosmetics/rest/locatorsearch"
    data = {
        "request": {
            "appkey": "A44D9C08-EA99-11E3-9D45-19A558203F82",
            "formdata": {
                "geoip": False,
                "dataview": "store_default",
                "google_autocomplete": "true",
                "limit": 250,
                "order": "rank, _DISTANCE",
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "",
                            "country": CurrentCountry,
                            "latitude": lat,
                            "longitude": lng,
                            "state": "",
                            "province": "",
                            "city": "",
                            "address1": "",
                            "postalcode": "",
                        }
                    ]
                },
                "searchradius": "10|25|50|100|250",
                "radiusuom": "mile",
                "where": {
                    "or": {
                        "webcat1": {"eq": "Y"},
                        "webcat2": {"eq": ""},
                        "webcat3": {"eq": ""},
                        "webcat4": {"eq": ""},
                        "webcat6": {"eq": ""},
                        "webcat7": {"eq": ""},
                    }
                },
                "false": "0",
            },
        }
    }

    stores = []
    stores_req = session.post(search_url, headers=headers, data=json.dumps(data))
    try:
        stores = json.loads(stores_req.text)["response"]["collection"]
    except:
        pass

    return stores, CurrentCountry


def process_record(raw_results_from_one_coordinate):
    stores, current_country = raw_results_from_one_coordinate
    for store in stores:
        if store["icon"] != "Nars":
            continue
        if store["uid"] in id_list:
            continue

        id_list.append(store["uid"])

        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["name"]
        street_address = store["address1"]
        if store["address2"] is not None and len(store["address2"]) > 0:
            street_address = street_address + ", " + store["address2"]

        city = store.get("city", "<MISSING>")
        state = store.get("state", "<MISSING>")
        zip = store.get("postalcode", "<MISSING>")
        country_code = store["country"]
        if country_code is None or country_code == "":
            country_code = current_country

        store_number = store["uid"]
        phone = store.get("phone", "<MISSING>")

        location_type = "<MISSING>"
        hours_list = []
        days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        for key in store.keys():
            if key in days:
                day = key
                time = store[day]
                if time is not None:
                    hours_list.append(day + ": " + time)

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
        countries = (
            SearchableCountries.WITH_ZIPCODE_AND_COORDS
            + SearchableCountries.WITH_COORDS_ONLY
        )

        totalCountries = len(countries)
        currentCountryCount = 0
        for country in countries:
            try:
                search = DynamicGeoSearch(
                    expected_search_radius_miles=100,
                    use_state=False,
                    country_codes=[country],
                )
                results = parallelize(
                    search_space=[
                        (
                            coord,
                            search.current_country(),
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
