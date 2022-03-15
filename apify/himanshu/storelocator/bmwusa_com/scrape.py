from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="bmwusa_com")


def fetch_data(sgw: SgWriter):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    max_distance = 1000

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        expected_search_radius_miles=max_distance,
    )

    for zip_code in search:
        if len(str(zip_code)) == 4:
            zip_code = "0" + str(zip_code)
        if len(str(zip_code)) == 3:
            zip_code = "00" + str(zip_code)
        log.info(
            "Searching: %s | Items remaining: %s" % (zip_code, search.items_remaining())
        )

        base_url = (
            "https://www.bmwusa.com/api/dealers/"
            + str(zip_code)
            + "/"
            + str(max_distance)
        )
        try:
            r = session.get(base_url, headers=headers)
        except:
            session = SgRequests()
            r = session.get(base_url, headers=headers)

        json_data = r.json()["Dealers"]
        for store_data in json_data:
            store = []
            store.append("https://www.bmwusa.com")
            store.append(store_data["DefaultService"]["Name"])
            store.append(store_data["DefaultService"]["Address"])
            store.append(store_data["DefaultService"]["City"])
            store.append(store_data["DefaultService"]["State"])
            store.append(store_data["DefaultService"]["ZipCode"])
            store.append("US")
            store.append(store_data["DefaultService"]["DealerShipUniqueID"])
            store.append(
                store_data["DefaultService"]["FormattedPhone"]
                if store_data["DefaultService"]["FormattedPhone"] != ""
                and store_data["DefaultService"]["FormattedPhone"] is not None
                else "<MISSING>"
            )
            if "CCRC" in store_data["DefaultService"]["Name"]:
                loc_type = "Certified Collision Repair Center"
            else:
                loc_type = "BMW CENTER"
            store.append(loc_type)
            latitude = store_data["DefaultService"]["LonLat"]["Lat"]
            longitude = store_data["DefaultService"]["LonLat"]["Lon"]
            if len(str(latitude)) < 4:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            else:
                search.found_location_at(latitude, longitude)
            store.append(latitude)
            store.append(longitude)
            hours = " ".join(
                list(
                    BeautifulSoup(
                        store_data["DefaultService"]["FormattedHours"], "lxml"
                    ).stripped_strings
                )
            )
            store.append(hours if hours != "" else "<MISSING>")
            link = store_data["DefaultService"]["Url"]
            if not link:
                link = "<MISSING>"
            store.append(link)

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
