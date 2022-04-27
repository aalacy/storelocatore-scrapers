import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.agrobanco.com.pe/"
    page_url = "https://www.agrobanco.com.pe/ubica-nuestras-oficinas/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath("//div/@data-offices"))
    js = json.loads(jsblock)
    for j in js:

        location_name = j.get("title") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        street_address = "".join(j.get("address")) or "<MISSING>"
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "PE"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = (
            "".join(j.get("phone"))
            .replace("615-0000", "6150000")
            .replace("Anx. ", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        if phone.find("-") != -1:
            phone = phone.split("-")[0].strip()
        if phone.find("Fax") != -1:
            phone = phone.split("Fax")[0].strip()
        hours_of_operation = j.get("hours") or "<MISSING>"

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
