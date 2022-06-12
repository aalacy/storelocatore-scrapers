from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.lush.com/api/gateway"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "lush.com"

    session = SgRequests()

    locs = [
        "UK",
        "UAE",
        "Australia",
        "hong kong",
        "japan",
        "new zealand",
        "Bahrain",
        "singapore",
        "malaysia",
        "saudi arabia",
        "thailand",
        "south korea",
    ]
    for loc in locs:
        off = -9
        for i in range(60):
            off = off + 9
            json = {
                "operationName": "yextGeoSearch",
                "variables": {"location": loc, "offset": off, "limit": 9},
                "query": "query yextGeoSearch($location: String!, $limit: Int, $offset: Int, $region: String) {\n  yextGeoSearch(\n    location: $location\n    offset: $offset\n    limit: $limit\n    region: $region\n  ) {\n    pagination {\n      total\n      has_more\n      page_token\n      __typename\n    }\n    locations {\n      address {\n        city\n        countryCode\n        extraDescription\n        line1\n        line2\n        line3\n        postalCode\n        region\n        sublocality\n        __typename\n      }\n      closed\n      description\n      distance {\n        distanceKilometers\n        distanceMiles\n        __typename\n      }\n      email\n      hours {\n        monday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        tuesday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        wednesday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        thursday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        friday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        saturday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        sunday {\n          openIntervals {\n            start\n            end\n            __typename\n          }\n          isClosed\n          __typename\n        }\n        __typename\n      }\n      id\n      latLng {\n        lat\n        lng\n        __typename\n      }\n      lastEdited\n      mainPhone\n      name\n      primaryImage {\n        alt\n        height\n        url\n        width\n        __typename\n      }\n      secondaryImage {\n        alt\n        height\n        url\n        width\n        __typename\n      }\n      services\n      slug\n      specialities\n      __typename\n    }\n    __typename\n  }\n}",
            }
            stores = session.post(base_link, headers=headers, json=json).json()["data"][
                "yextGeoSearch"
            ]["locations"]

            if len(stores) == 0:
                break
            for store in stores:
                location_name = store["name"].strip()

                raw_address = store["address"]
                try:
                    street_address = (
                        raw_address["line1"] + " " + raw_address["line2"]
                    ).strip()
                except:
                    street_address = raw_address["line1"]
                city = raw_address["city"]
                state = "<MISSING>"
                zip_code = raw_address["postalCode"]
                country_code = raw_address["countryCode"]
                store_number = store["id"].replace("'", "")
                phone = store["mainPhone"]
                latitude = store["latLng"]["lat"]
                longitude = store["latLng"]["lng"]
                location_type = "<MISSING>"
                link = (
                    "https://www.lush.com/uk/en/shops/"
                    + store["slug"]
                    + "?id="
                    + store_number
                )

                hours = ""
                raw_hours = store["hours"]
                if not raw_hours:
                    hours = "<MISSING>"
                else:
                    for day in raw_hours:
                        if "day" not in day:
                            continue
                        try:
                            clean_hours = (
                                raw_hours[day]["openIntervals"][0]["start"]
                                + "-"
                                + raw_hours[day]["openIntervals"][0]["end"]
                            )
                        except:
                            clean_hours = "Closed"
                        hours = (hours + " " + day.title() + " " + clean_hours).strip()
                    hours = hours.replace("  ", " ")

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
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
                        hours_of_operation=hours,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
