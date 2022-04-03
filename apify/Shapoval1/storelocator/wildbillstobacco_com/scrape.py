from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.wildbillstobacco.com"
    api_url = f"https://www.wildbillstobacco.com/wp-admin/admin-ajax.php?action=store_search&lat={str(lat)}&lng={str(long)}&max_results=150&search_radius=500&search=Negaunee%2C%20MI%2049866%2C%20USA&statistics="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()

    for j in js:

        page_url = j.get("permalink")
        location_name = (
            "".join(j.get("store"))
            .replace("&#8217;", "`")
            .replace("&#038;", "&")
            .replace("&#8211;", "-")
            .strip()
        )
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "USA"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours_of_operation = "<MISSING>"
        hours = j.get("hours") or "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
        if location_name.find("CLOSED") != -1:
            hours_of_operation = "Closed"

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
