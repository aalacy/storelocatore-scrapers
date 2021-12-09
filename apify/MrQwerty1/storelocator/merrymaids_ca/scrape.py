from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    locator_domain = "https://merrymaids.ca/"
    api_url = "https://merrymaids.ca/wp-admin/admin-ajax.php?action=store_search&lat=49.9145556&lng=-97.2116967&max_results=250&search_radius=5000&autoload=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        page_url = "https://merrymaids.ca/locations"
        location_name = "".join(j.get("store")).replace("&#038;", "&").strip()
        street_address = j.get("address")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = "".join(j.get("phone")).replace("(Kentville)", "").strip()
        hours_of_operation = j.get("hours")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
