import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.afbasket.com"
    page_url = "https://www.afbasket.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    block = r.text.split("var locations =")[1].split(";")[0]
    js = json.loads(block)

    for j in js:

        street_address = j.get("address1")
        city = j.get("city")
        postal = j.get("zipCode")
        state = j.get("state")
        country_code = "US"
        store_number = j.get("storeNumber")
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours = j.get("hourInfo") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*//text()"))
                .replace("\n", "")
                .split("4th")[0]
                .strip()
            )

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
