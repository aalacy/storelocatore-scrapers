from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://mysprintfs.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "locations")]/text()'))
        .split("locations = [")[1]
        .split("];")[0]
        .strip()
    )
    jsblock = " ".join(jsblock.split())
    js = eval(jsblock)

    for j in js:
        page_url = "https://mysprintfs.com/locations"
        location_name = j.get("title")
        street_address = (
            "".join(j.get("address")).replace(",", "").strip() or "<MISSING>"
        )
        if street_address == "<MISSING>":
            continue
        state = "<MISSING>"
        postal = j.get("zip")
        country_code = "USA"
        city = "".join(j.get("city")) or "<MISSING>"
        if city.find(",") != -1:
            city = city.split(",")[0].strip()
        ad = "".join(j.get("city"))
        if ad.find(",") != -1:
            state = ad.split(",")[1].strip()
        store_number = j.get("count")
        latitude = j.get("coordinates")[0]
        longitude = j.get("coordinates")[1]
        phone = j.get("phone")
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
    locator_domain = "https://mysprintfs.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
