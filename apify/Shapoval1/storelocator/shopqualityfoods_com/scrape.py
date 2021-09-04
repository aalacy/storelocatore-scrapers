from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://shopqualityfoods.com"
    page_url = "https://api.freshop.com/1/stores?app_key=quality_foods&has_address=true&is_selectable=true&limit=100&token=7975953ee68f37b8418eaa83b9c00c4e"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    js = r.json()
    for j in js["items"]:
        page_url = (
            j.get("url") or "https://www.shopqualityfoods.com/my-store/store-locator"
        )
        location_name = j.get("name")
        street_address = j.get("address_1")
        phone = "".join(j.get("phone_md")).replace("Phone:", "").strip()
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "US"
        city = j.get("city")
        store_number = j.get("store_number")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = "".join(j.get("hours_md")).replace("\n", " ").strip()

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


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
