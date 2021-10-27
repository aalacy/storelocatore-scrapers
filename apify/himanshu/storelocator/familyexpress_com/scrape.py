from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):
    base_url = "https://familyexpress.com/api/locations/place"
    r = session.get(base_url).json()["places"]
    for location in r:
        if location["yextData"]:
            try:
                if "isClosed" not in location["yextData"]["hours"]["sunday"]:
                    hours = (
                        " sunday : "
                        + location["yextData"]["hours"]["sunday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["sunday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours = " sunday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["monday"]:
                    hours += (
                        " monday : "
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " monday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["monday"]:
                    hours += (
                        " monday : "
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["monday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " tuesday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["tuesday"]:
                    hours += (
                        " tuesday : "
                        + location["yextData"]["hours"]["tuesday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["tuesday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " wednesday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["wednesday"]:
                    hours += (
                        " wednesday : "
                        + location["yextData"]["hours"]["wednesday"]["openIntervals"][
                            0
                        ]["start"]
                        + "-"
                        + location["yextData"]["hours"]["wednesday"]["openIntervals"][
                            0
                        ]["end"]
                    )
                else:
                    hours += " wednesday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["thursday"]:
                    hours += (
                        " thursday : "
                        + location["yextData"]["hours"]["thursday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["thursday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " thursday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["friday"]:
                    hours += (
                        " friday : "
                        + location["yextData"]["hours"]["friday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["friday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " friday : Closed"
                if "isClosed" not in location["yextData"]["hours"]["saturday"]:
                    hours += (
                        " saturday : "
                        + location["yextData"]["hours"]["saturday"]["openIntervals"][0][
                            "start"
                        ]
                        + "-"
                        + location["yextData"]["hours"]["saturday"]["openIntervals"][0][
                            "end"
                        ]
                    )
                else:
                    hours += " saturday : Closed"
            except:
                hours = "<MISSING>"
            try:
                phone = location["yextData"]["mainPhone"]
            except KeyError:
                phone = "<MISSING>"

            try:
                location_name = location["yextData"]["c_subName"]
            except:
                continue

            street_address = location["yextData"]["address"]["line1"]
            city = location["yextData"]["address"]["city"]
            state = location["yextData"]["address"]["region"]
            zip_code = location["yextData"]["address"]["postalCode"]
            country_code = location["yextData"]["address"]["countryCode"]
            store_number = location["storeId"]
            location_type = ""
            latitude = location["yextData"]["yextDisplayCoordinate"]["latitude"]
            longitude = location["yextData"]["yextDisplayCoordinate"]["longitude"]

            sgw.write_row(
                SgRecord(
                    locator_domain="https://familyexpress.com",
                    page_url="https://familyexpress.com/locations",
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
                    hours_of_operation=hours.strip(),
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
