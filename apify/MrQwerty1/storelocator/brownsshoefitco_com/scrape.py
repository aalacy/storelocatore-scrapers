from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://brownsshoefitco.locally.com/stores/conversion_data"
    r = session.get(api, params=params, headers=headers)
    js = r.json()["markers"]

    for j in js:
        location_name = j.get("name")
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        store_number = j.get("id")
        page_url = f'https://stores.brownsshoefitcompany.com/{j.get("slug")}'
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        days = j.get("display_dow") or {}
        for d in days.values():
            day = d.get("label")
            inter = d.get("bil_hrs")
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://brownsshoefitcompany.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    params = (
        ("has_data", "true"),
        ("company_id", "12247"),
        ("inline", "1"),
        ("map_center_lat", "39.65780487864641"),
        ("map_center_lng", "-96.3291944123471"),
        ("map_distance_diag", "507.1332170273249"),
        ("sort_by", "proximity"),
        ("no_variants", "0"),
        ("only_retailer_id", "12247"),
    )
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
