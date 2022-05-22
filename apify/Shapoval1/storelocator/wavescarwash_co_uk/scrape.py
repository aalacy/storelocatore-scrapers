from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://customer.waveswebapp.co.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    data = {
        "latitude": f"{lat}",
        "longitude": f"{long}",
        "includeDeclineCustomerBookingSites": "true",
        "onlySitesWithPromotions": "false",
        "includeClosedSites": "true",
    }
    session = SgRequests()

    r = session.post(
        "https://customer.waveswebapp.co.uk/booking/ajaxsearchsitesbylocation",
        headers=headers,
        data=data,
    )

    js = r.json()["Results"]

    for j in js:

        page_url = "https://wavescarwash.co.uk/car-wash-locator.html"
        location_name = "".join(j.get("SiteName")).strip() or "<MISSING>"
        street_address = f"{j.get('AddressLine1')} {j.get('AddressLine2')}".strip()
        if "Tesco Store" in str(j.get("AddressLine1")):
            street_address = j.get("AddressLine2")
        city = j.get("AddressLine4") or "<MISSING>"
        if city == "<MISSING>":
            city = j.get("AddressLine3") or "<MISSING>"
        if str(city).find(",") != -1:
            city = str(city).split(",")[1].strip()
        postal = j.get("Postcode") or "<MISSING>"
        country_code = "UK"
        phone = j.get("PhoneNumber") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for d in days:
            day = d
            time = j.get(f"OpeningHours_{d}")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=50,
        expected_search_radius_miles=50,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
