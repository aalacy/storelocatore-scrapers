from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sams.com.mx"
    api_url = "https://www.sams.com.mx/rest/model/atg/userprofiling/ProfileActor/stateStoreLocator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["stateStores"].keys():
        key = j
        for l in js["stateStores"][f"{key}"]:
            slug = l.get("storeId")
            city = l.get("city") or "<MISSING>"
            page_url = f"https://www.sams.com.mx/clubes/{slug}"
            location_name = l.get("name") or "<MISSING>"
            street_address = "".join(l.get("address1")).strip()
            if street_address.find("(") != -1:
                street_address = street_address.split("(")[0].strip()
            state = l.get("state") or "<MISSING>"
            postal = l.get("postalCode") or "<MISSING>"
            country_code = l.get("country") or "Mexico"
            latitude = l.get("latitude") or "<MISSING>"
            longitude = l.get("longitude") or "<MISSING>"
            phone = l.get("phoneNumber") or "<MISSING>"
            if phone == "(55) 55":
                phone = "<MISSING>"
            hours_of_operation = l.get("hours") or "<MISSING>"

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
