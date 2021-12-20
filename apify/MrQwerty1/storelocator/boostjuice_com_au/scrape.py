from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        expected_search_radius_miles=10,
    )
    for lat, lng in search:
        api = f"https://www.boostjuice.com.au/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}"
        r = session.get(api, headers=headers)
        js = r.json()

        for j in js:
            page_url = j.get("url")
            location_name = j.get("store")
            street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zip")
            store_number = j.get("id")
            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("lng")

            _tmp = []
            hours = j.get("openhours") or "<html></html>"
            tree = html.fromstring(hours)
            tr = tree.xpath("//li")

            for t in tr:
                day = "".join(t.xpath("./em//text()")).strip()
                time = "".join(t.xpath("./text()")).strip()
                _tmp.append(f"{day}: {time}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="AU",
                phone=phone,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.boostjuice.com.au/"
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
