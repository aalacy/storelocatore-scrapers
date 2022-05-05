from sgrequests import SgRequests

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("woodspring_com")
session = SgRequests()


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=200,
        expected_search_radius_miles=200,
    )
    logger.info(f"remaining coordinates: {coords.items_remaining()}")
    main_url = "https://www.woodspring.com"
    addresses = []
    for cord in coords:
        logger.info(str(cord))
        result_coords = []
        x = cord[0]
        y = cord[1]
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        }
        r = session.get(
            "https://www-api.woodspring.com/v2/hotel/hotels?lat="
            + str(x)
            + "&lng="
            + str(y)
            + "&max=200&offset=0&radius=200"
        )
        if "searchResults" not in r.json():
            continue
        data = r.json()["searchResults"]
        for store_data in data:
            result_coords.append(
                (
                    store_data["geographicLocation"]["latitude"],
                    store_data["geographicLocation"]["longitude"],
                )
            )
            if (
                store_data["address"]["countryCode"] != "US"
                and store_data["address"]["countryCode"] != "CA"
            ):
                continue
            store = []
            store.append(main_url)
            logger.info(store_data["hotelName"])
            store.append(store_data["hotelName"])
            location_request = session.get(
                "https://www-api.woodspring.com/v2/hotel/hotels/"
                + str(store_data["hotelId"])
                + "?include=location,phones,amenities,contacts,occupancy,policies,presell,rooms",
                headers=headers,
            )
            location_data = location_request.json()
            if "hotelStatus" in location_data["hotelInfo"]["hotelSummary"]:
                if (
                    location_data["hotelInfo"]["hotelSummary"]["hotelStatus"]
                    == "Closed"
                ):
                    continue
            add = location_data["hotelInfo"]["hotelSummary"]["addresses"][0]
            try:
                if (
                    str(location_data["hotelInfo"]["hotelSummary"]["phones"][0]["tech"])
                    == "1"
                ):
                    phone = location_data["hotelInfo"]["hotelSummary"]["phones"][0][
                        "number"
                    ]
                else:
                    phone = location_data["hotelInfo"]["hotelSummary"]["phones"][-1][
                        "number"
                    ]
            except:
                phone = location_data["hotelInfo"]["hotelSummary"]["phones"][-1][
                    "number"
                ]
            store.append(",".join(add["street"]))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(add["cityName"] if add["cityName"] else "<MISSING>")
            if "," + store[-1] + "," in store[2]:
                store[2] = store[2].split("," + store[-1])[0]
            store.append(
                add["subdivisionCode"] if add["subdivisionCode"] else "<MISSING>"
            )
            store.append(add["postalCode"] if add["postalCode"] else "<MISSING>")
            store.append(add["countryCode"])
            store.append(store_data["hotelId"])
            store.append(
                phone.replace("111111111", "(863) 578-3658").replace(
                    "13213681", "<MISSING>"
                )
            )
            store.append("<MISSING>")
            store.append(store_data["geographicLocation"]["latitude"])
            store.append(store_data["geographicLocation"]["longitude"])
            rows = location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"]
            for i in range(len(rows)):
                if "hoursOfOperation" in rows[i]:
                    try:
                        row = i
                        if (
                            "hoursOfOperation"
                            in location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][-1]
                        ):
                            pass
                        elif (
                            "hoursOfOperation"
                            in location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][-2]
                        ):
                            row = -2
                        mon = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["mon"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["mon"][0]["endTime"]
                        )
                        tue = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["tue"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["tue"][0]["endTime"]
                        )
                        wed = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["wed"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["wed"][0]["endTime"]
                        )
                        thu = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["thu"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["thu"][0]["endTime"]
                        )
                        fri = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["fri"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["fri"][0]["endTime"]
                        )
                        sat = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["sat"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["sat"][0]["endTime"]
                        )
                        sun = (
                            location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["sun"][0]["startTime"]
                            + "-"
                            + location_data["hotelInfo"]["hotelSummary"][
                                "hotelAmenities"
                            ][row]["hoursOfOperation"]["sun"][0]["endTime"]
                        )
                        hoo = (
                            "mon "
                            + mon
                            + ", tue "
                            + tue
                            + ", wed "
                            + wed
                            + ", thu "
                            + thu
                            + ", fri "
                            + fri
                            + ", sat "
                            + sat
                            + ", sun "
                            + sun
                        )
                    except:
                        try:
                            if (
                                str(
                                    location_data["hotelInfo"]["hotelSummary"][
                                        "hotelAmenities"
                                    ][row]["hoursOfOperation"]
                                ).count("True")
                                == 7
                            ):
                                hoo = "Daily 24 Hours"
                        except:
                            hoo = ""

            store.append(hoo)
            store.append(main_url + str(store_data["hotelUri"]))

            sgw.write_row(
                SgRecord(
                    locator_domain=store[0],
                    location_name=store[1],
                    street_address=store[2],
                    city=store[3],
                    state=store[4],
                    zip_postal=store[5],
                    country_code=store[6],
                    store_number=store[7],
                    phone=store[8],
                    location_type=store[9],
                    latitude=store[10],
                    longitude=store[11],
                    hours_of_operation=store[12],
                    page_url=store[13],
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
