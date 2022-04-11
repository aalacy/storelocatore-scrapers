from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://newbalance.cl/"
    api_url = "https://newbalance.cl/mack/api/branches/?_=1649412792069"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://newbalance.cl/tiendas"
        slug = "".join(j.get("name"))
        location_name = "New Balance Stores"
        if slug.find("Outlet") != -1:
            location_name = "New Balance Outlet"
        location_type = "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        country_code = "CL"
        city = j.get("commune") or "<MISSING>"
        store_number = j.get("store_id") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
