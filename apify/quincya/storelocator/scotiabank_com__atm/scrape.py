from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("scotiabank_com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    max_results = 50
    max_distance = None
    dup_tracker = []
    total = 0
    locator_domain = "scotiabank.com"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )
    for lat, lng in search:
        base_link = (
            "https://mapsms.scotiabank.com/branches?1=1&latitude=%s&longitude=%s&recordlimit=%s&locationtypes=1,2,3"
            % (lat, lng, max_results)
        )
        try:
            stores = session.get(base_link, headers=headers).json()["branchInfo"][
                "marker"
            ]
        except Exception:
            continue
        logger.info(f"Pulling the data from: {base_link}")
        found = 0
        for store in stores:
            store_number = store["@attributes"]["id"]
            latitude = store["@attributes"]["lat"]
            longitude = store["@attributes"]["lng"]

            search.found_location_at(latitude, longitude)
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)

            location_name = store["name"]
            location_type = (
                "Branch"
                if store["@attributes"]["type"] == "1"
                else "ABM"
                if store["@attributes"]["type"] == "3"
                else store["@attributes"]["type"]
            )
            street_address = " ".join(store["address"].split(",")[:-3])
            city = store["address"].split(",")[-3].strip()
            if len(store["address"].split(",")[-2].split()) > 1:
                state = store["address"].split(",")[-2].strip()[:-7].strip()
                zip_code = store["address"].split(",")[-2].strip()[-7:].strip()
            else:
                state = store["address"].split(",")[-2].strip()
                zip_code = "<MISSING>"
            country_code = "CA"
            phone = store["phoneNo"]
            if not phone:
                phone = "<MISSING>"

            hours = store["hours"]
            hours_of_operation = ""
            for day in hours:
                try:
                    day_hr = hours[day]["open"] + "-" + hours[day]["close"]
                except:
                    day_hr = "Closed"
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + day_hr
                ).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "<MISSING>"

            found += 1

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url="<MISSING>",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )
        total += found
    logger.info(f"Scraping Finished | Total Store Count:{total}")


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
