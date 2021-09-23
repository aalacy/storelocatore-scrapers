import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in search:
        api = f"https://stores.rainbowshops.com/umbraco/api/location/GetDataByCoordinates?longitude={lng}&latitude={lat}&distance=100&units=miles"
        r = session.get(api)
        js = json.loads(r.json())["StoreLocations"]

        for j in js:
            l = j.get("Location") or {}
            e = j.get("ExtraData") or {}
            a = e.get("Address") or {}
            coords = l.get("coordinates") or [SgRecord.MISSING, SgRecord.MISSING]
            longitude, latitude = coords

            location_name = j.get("Name") or SgRecord.MISSING
            store_number = e.get("ReferenceCode")
            street_address = f'{a.get("AddressNonStruct_Line1")} {a.get("AddressNonStruct_Line2") or ""}'.strip()
            city = a.get("Locality")
            state = a.get("Region") or a.get("CountryCode")
            postal = a.get("PostalCode")
            country_code = "US"
            phone = e.get("Phone")
            page_url = f"https://stores.rainbowshops.com/{state}/{city}/{store_number}/"

            _tmp = []
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            hours = e.get("HoursOfOperations")
            if hours:
                for day, hour in zip(days, hours.split("|")):
                    _tmp.append(f"{day}: {hour}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://rainbowshops.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
