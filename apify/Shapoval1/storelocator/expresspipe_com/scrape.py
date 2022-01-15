from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://expresspipe.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://expresspipe.reece.com/",
        "content-type": "application/json",
        "authorization": "",
        "Origin": "https://expresspipe.reece.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    session = SgRequests()

    data = (
        '{"operationName":"findBranches","variables":{"branchSearch":{"latitude":'
        + str(lat)
        + ',"longitude":'
        + str(long)
        + ',"count":20}},"query":"query findBranches($branchSearch: BranchSearch!) {\\n  branchSearch(branchSearch: $branchSearch) {\\n    latitude\\n    longitude\\n    branches {\\n      ...Branch\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment Branch on Branch {\\n  branchId\\n  name\\n  entityId\\n  address1\\n  address2\\n  city\\n  state\\n  zip\\n  phone\\n  distance\\n  erpSystemName\\n  website\\n  workdayId\\n  workdayLocationName\\n  actingBranchManager\\n  actingBranchManagerPhone\\n  actingBranchManagerEmail\\n  businessHours\\n  latitude\\n  longitude\\n  isPlumbing\\n  isWaterworks\\n  isHvac\\n  isBandK\\n  __typename\\n}\\n"}'
    )

    r = session.post("https://api.reece.com/", headers=headers, data=data)
    try:
        js = r.json()["data"]["branchSearch"]["branches"]
    except AttributeError:
        return

    for j in js:

        page_url = "https://expresspipe.reece.com/location-search"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        hours_of_operation = j.get("businessHours") or "<MISSING>"
        location_type = j.get("__typename")
        store_number = j.get("branchId") or "<MISSING>"
        isPlumbing = j.get("isPlumbing")
        isWaterworks = j.get("isWaterworks")
        isHvac = j.get("isHvac")
        isBandK = j.get("isBandK")
        if isPlumbing:
            location_type = "Plumbing"
        if isWaterworks:
            location_type = "Waterworks"
        if isHvac:
            location_type = "Hvac"
        if isBandK:
            location_type = "Showroom"

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=70,
        expected_search_radius_miles=70,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=7) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
