from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://daylightdonuts.com/"
    api_url = f"https://daylightdonuts.com/wp-admin/admin-ajax.php?action=store_search&lat={str(lat)}&lng={str(long)}&max_results=10000&search_radius=250000&autoload=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        page_url = "https://daylightdonuts.com/find-your-daylight/"
        location_name = j.get("store") or "<MISSING>"
        location_name = (
            str(location_name).replace("&#038;", "&").replace("&#8217;", "’")
        )
        store_number = j.get("id") or "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        location_type = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if str(phone).find("or") != -1:
            phone = str(phone).split("or")[0].strip()
        if phone == "TBA":
            phone = "<MISSING>"
        if phone == "COMING SOON":
            phone = "<MISSING>"
            location_type = "COMING SOON"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("hours")
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
            SgRecordID({SgRecord.Headers.STORE_NUMBER}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
