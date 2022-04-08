from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.huntington.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    session = SgRequests()

    data = {
        "longitude": f"{str(long)}",
        "latitude": f"{str(lat)}",
        "typeFilter": "1,2",
        "envelopeFreeDepositsFilter": "false",
        "timeZoneOffset": "-180",
        "scController": "GetLocations",
        "scAction": "GetLocationsList",
    }

    r = session.post(
        "https://www.huntington.com/post/GetLocations/GetLocationsList",
        headers=headers,
        data=data,
    )

    js = r.json()["features"]

    for j in js:
        a = j.get("properties")
        page_url = "https://www.huntington.com/branchlocator"
        location_name = a.get("LocName") or "<MISSING>"
        street_address = a.get("LocStreet") or "<MISSING>"
        city = a.get("LocCity") or "<MISSING>"
        state = a.get("LocState") or "<MISSING>"
        postal = a.get("LocZip") or "<MISSING>"
        country_code = "US"
        phone = a.get("LocPhone") or "<MISSING>"
        latitude = j.get("geometry").get("coordinates")[1]
        longitude = j.get("geometry").get("coordinates")[0]
        hours_of_operation = "<MISSING>"
        location_type = a.get("LocType") or "<MISSING>"
        if location_type == "1":
            location_type = "Branch"
        if location_type == "2":
            location_type = "ATM"
        store_number = a.get("LocID") or "<MISSING>"
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        tmp = []
        if a.get("SundayLobbyHours"):
            for d in days:
                day = d
                times = a.get(f"{d}LobbyHours")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        if hours_of_operation.count("24 Hours") == 7:
            hours_of_operation = "24 Hours"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=30,
        expected_search_radius_miles=30,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
