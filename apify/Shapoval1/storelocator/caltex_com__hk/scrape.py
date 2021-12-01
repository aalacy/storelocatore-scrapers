from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.caltex.com/hk/en/"
    api_url = "https://www.caltex.com/bin/services/getStations.json?pagePath=/content/caltex/hk/en/find-a-caltex-station&siteType=b2c"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.caltex.com/hk/en/find-a-caltex-station.html"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("siteType") or "<MISSING>"
        street_address = "".join(j.get("street")) or "<MISSING>"
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "HK"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phoneNumber") or "<MISSING>"
        hours_of_operation = j.get("operatingHours") or "<MISSING>"

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
            location_type=location_type,
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
