from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.com.au/"
    api_url = "https://www.honda.com.au/api/locateDealer/Dealerships/get?lat=&lon="
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        slug = j.get("Website")
        page_url = f"https://www.honda.com.au{slug}"
        location_name = j.get("Name")
        location_type = j.get("Locations")[0].get("Type")
        street_address = (
            str(j.get("Locations")[0].get("AddressLine1"))
            .replace("Shop 2117, Level 2, Indooroopilly Shopping Centre,", "")
            .strip()
        )
        state = j.get("Locations")[0].get("AddressState")
        postal = j.get("Locations")[0].get("AddressPostcode")
        country_code = "AU"
        city = j.get("Locations")[0].get("AddressSuburb")
        store_number = j.get("Locations")[0].get("Id")
        latitude = j.get("Locations")[0].get("Latitude")
        longitude = j.get("Locations")[0].get("Longitude")
        phone = j.get("Locations")[0].get("Phone")
        hours_of_operation = "<MISSING>"
        hours = j.get("Locations")[0].get("workingHoursFormatted") or "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
