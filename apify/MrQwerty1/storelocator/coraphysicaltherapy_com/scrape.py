from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(la, ln, sgw: SgWriter):
    api = f"https://www.coraphysicaltherapy.com/wp-admin/admin-ajax.php?action=store_search&lat={la}&lng={ln}&autoload=1"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        page_url = j.get("permalink")
        location_name = j.get("store").strip()
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = j.get("id")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        hours = j.get("hours") or "<html></html>"
        tree = html.fromstring(hours)
        tr = tree.xpath("//tr")

        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            time = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.coraphysicaltherapy.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=50,
        max_search_distance_miles=200,
        max_search_results=20,
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for lat, lon in search:
            fetch_data(lat, lon, writer)
