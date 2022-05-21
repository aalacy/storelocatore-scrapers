from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.kuhnsmarket.com/flyerapp/api/stores"
    page_url = "https://kuhnsmarket.com/locations"
    r = session.get(api)

    for j in r.json():
        location_name = j.get("abdisplayname")
        street_address = f'{j.get("adaddress1")} {j.get("adaddress2") or ""}'.strip()
        city = j.get("adcity")
        state = j.get("adstate")
        postal = j.get("adzip")
        phone = j.get("abworkphone")
        store_number = j.get("id")
        hours = j.get("storehourshtml") or ""
        hours_of_operation = hours.replace("<br />", ";")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://kuhnsmarket.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
