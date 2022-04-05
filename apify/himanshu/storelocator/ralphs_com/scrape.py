from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_1_KM

log = SgLogSetup().get_logger("ralphs_com")


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    locator_domain = "https://www.ralphs.com/"

    max_distance = 40
    max_results = 50

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=max_distance,
        expected_search_radius_miles=max_distance,
        max_search_results=max_results,
        granularity=Grain_1_KM(),
    )

    for zip_code in search:
        base_link = (
            "https://www.ralphs.com/atlas/v1/stores/v1/search?filter.query="
            + str(zip_code)
        )
        r = session.get(base_link, headers=headers)
        try:
            data_store = r.json()["data"]["storeSearch"]["results"]
        except:
            continue

        for key in data_store:
            try:
                location_name = key["vanityName"] + " " + key["facilityName"]
            except:
                location_name = key["vanityName"]

            raw_address = key["address"]["address"]
            street_address = " ".join(raw_address["addressLines"]).strip()
            city = raw_address["cityTown"]
            state = raw_address["stateProvince"]
            zipp = raw_address["postalCode"]
            country_code = raw_address["countryCode"]
            store_number = key["storeNumber"]
            try:
                phone = key["phoneNumber"]
            except:
                phone = ""
            if key["banner"]:
                location_type = key["banner"]
            else:
                location_type = "store"
            latitude = key["location"]["lat"]
            longitude = key["location"]["lng"]
            if str(latitude) == "0":
                latitude = ""
                longitude = ""
            else:
                search.found_location_at(latitude, longitude)
            hours = ""
            try:
                raw_hours = key["formattedHours"]
                for raw_hour in raw_hours:
                    hours = (
                        hours
                        + " "
                        + raw_hour["displayName"]
                        + " "
                        + raw_hour["displayHours"]
                    ).strip()
                hours = hours.replace("  ", " ")
            except:
                pass
            page_url = (
                "https://www.ralphs.com/stores/details/"
                + str(key["divisionNumber"])
                + "/"
                + str(store_number)
            )

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours,
                )
            )

        # fuel store
        try:
            datas1 = r.json()["data"]["storeSearch"]["fuelResults"]
        except:
            continue
        for key1 in datas1:
            try:
                location_name = key1["vanityName"] + " " + key1["facilityName"]
            except:
                location_name = key1["vanityName"]

            raw_address = key1["address"]["address"]
            street_address = " ".join(raw_address["addressLines"]).strip()
            city = raw_address["cityTown"]
            state = raw_address["stateProvince"]
            zipp = raw_address["postalCode"]
            country_code = raw_address["countryCode"]
            store_number = key1["storeNumber"]
            try:
                phone = key1["phoneNumber"]
            except:
                phone = ""
            if key1["banner"]:
                location_type = key1["banner"]
            else:
                location_type = "fuel"
            latitude = key1["location"]["lat"]
            longitude = key1["location"]["lng"]

            hours = ""
            try:
                raw_hours = key1["formattedHours"]
                for raw_hour in raw_hours:
                    hours = (
                        hours
                        + " "
                        + raw_hour["displayName"]
                        + " "
                        + raw_hour["displayHours"]
                    ).strip()
                hours = hours.replace("  ", " ")
            except:
                pass
            if key1["open24Hours"]:
                hours = "24 Hours"
            page_url = (
                "https://www.ralphs.com/stores/details/"
                + str(key1["divisionNumber"])
                + "/"
                + str(store_number)
            )
            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours,
                )
            )


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.LOCATION_NAME,
                SgRecord.Headers.STREET_ADDRESS,
                SgRecord.Headers.CITY,
                SgRecord.Headers.LOCATION_TYPE,
            }
        )
    )
) as writer:
    fetch_data(writer)
