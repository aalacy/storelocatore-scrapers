import time
from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_4

log = SgLogSetup().get_logger("meijer.com")


def fetch_data(sgw: SgWriter):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    max_distance = 100
    max_results = 10

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        expected_search_radius_miles=max_distance,
        max_search_results=max_results,
        granularity=Grain_4(),
    )

    locator_domain = "meijer.com"

    dup_tracker = []

    for postcode in search:
        log.info(
            "Searching: %s | Items remaining: %s" % (postcode, search.items_remaining())
        )
        base_link = (
            "https://www.meijer.com/bin/meijer/store/search?locationQuery=%s&radius=%s"
            % (postcode, max_distance)
        )

        log.info(base_link)
        try:
            stores = session.get(base_link, headers=headers).json()["pointsOfService"]
        except:
            try:
                session = SgRequests()
                time.sleep(5)
                stores = session.get(base_link, headers=headers).json()[
                    "pointsOfService"
                ]
            except:
                log.info("Error..No stores!")
                continue

        for store in stores:
            location_name = store["displayName"]
            street_address = (
                store["address"]["line1"].replace("?", "'").split("(")[0].strip()
            )
            city = store["address"]["town"]
            state = store["address"]["region"]["isocode"].replace("US-", "")
            zip_code = store["address"]["postalCode"]
            country_code = "US"
            latitude = store["geoPoint"]["latitude"]
            longitude = store["geoPoint"]["longitude"]
            search.found_location_at(latitude, longitude)
            store_number = store["name"]
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)

            link = "https://www.meijer.com/bin/meijer/store/details?storeId=" + str(
                store_number
            )
            store_det = session.get(link, headers=headers).json()[
                "storeLocatorFeatures"
            ]

            phone = ""
            location_type = ""
            hours_of_operation = ""
            for i in store_det:
                if location_type:
                    location_type = (
                        location_type + ", " + i["storeFeatureServiceType"]
                    ).strip()
                else:
                    location_type = i["storeFeatureServiceType"]
                if "Pharmacy".upper() in i["storeFeatureServiceType"].upper():
                    if i["openingSchedule"]["is24Hrsand365Days"]:
                        hours_of_operation = "24hrs Daily"
                    else:
                        raw_hours = i["openingSchedule"]["weekDayOpeningList"]
                        for raw_hour in raw_hours:
                            day = raw_hour["weekDay"]
                            if raw_hour["closed"]:
                                day_hours = day + " Closed"
                            else:
                                open_ = raw_hour["openingTime"]["formattedHour"]
                                close = raw_hour["closingTime"]["formattedHour"]
                                day_hours = day + " " + open_ + "-" + close
                            hours_of_operation = (
                                hours_of_operation + " " + day_hours
                            ).strip()
                    try:
                        phone = i["phone"]
                    except:
                        phone = ""

            if "pharmacy" not in location_type.lower():
                continue
            if not phone:
                try:
                    phone = store["phone"]
                except:
                    phone = ""
            page_url = (
                "https://www.meijer.com/shopping/store-locator/"
                + str(store_number)
                + ".html"
            )

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
