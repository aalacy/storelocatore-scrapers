from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.caltex.com/ph/"
    api_url = "https://www.caltex.com/bin/services/getStations.json?pagePath=/content/caltex/ph/en/find-us&siteType=b2c"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.caltex.com/ph/find-us.html"
        location_name = j.get("name") or "<MISSING>"
        location_type = j.get("siteType") or "<MISSING>"
        ad = "".join(j.get("street"))
        a = parse_address(International_Parser(), ad)
        street_address = j.get("street") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "PH"
        city = j.get("city") or "<MISSING>"
        if city == "<MISSING>":
            city = a.city or "<MISSING>"
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
