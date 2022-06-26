from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.mos.jp/data/shop/shop.json"
    r = session.get(api, headers=headers)
    js = r.json()["shops"]

    for j in js:
        raw_address = j.get("addr_all")
        street_address = j.get("addr")
        city = j.get("city_name")
        state = j.get("pref_name")
        postal = f'{j.get("zip1") or ""}-{j.get("zip2") or ""}'.strip()
        if postal == "-":
            postal = SgRecord.MISSING
        country_code = "JP"
        store_number = j.get("shop_cd")
        location_name = j.get("name")
        page_url = f"https://netorder.mos.co.jp/pc/shop_detail/{store_number}/"
        phone = (
            f'{j.get("tel1") or ""}-{j.get("tel2") or ""}-{j.get("tel3") or ""}'.strip()
        )
        if phone == "--":
            phone = SgRecord.MISSING
        latitude = j.get("lat")
        longitude = j.get("lon")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation="<INACCESSIBLE>",
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.mos.jp/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)
