from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=100
    )
    for lat, lng in search:
        api = f"https://spiritleaf.ca/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&search_radius=9999&autoload=1"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            page_url = j.get("permalink")
            location_name = j.get("store") or ""
            location_name = location_name.replace("&#8211;", "-").replace(
                "&#8217;", "'"
            )
            street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zip")
            phone = j.get("phone")
            store_number = j.get("id")
            latitude = j.get("lat")
            longitude = j.get("lng")

            _tmp = []
            source = j.get("hours") or "<html></html>"
            tree = html.fromstring(source)
            tr = tree.xpath("//tr")
            for t in tr:
                day = "".join(t.xpath("./td[1]/text()")).strip()
                time = "".join(t.xpath("./td[2]//text()")).strip()
                _tmp.append(f"{day}: {time}")

            hours_of_operation = ";".join(_tmp)
            status = j.get("terms") or ""
            if "coming" in status.lower():
                hours_of_operation = "Coming Soon"

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="CA",
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://spiritleaf.ca/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
