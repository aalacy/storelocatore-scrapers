import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.rs"
    api_url = "https://www.kfc.rs/restorani/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "places")]/text()'))
        .split('"places":')[1]
        .split(',"styles":"')[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:
        b = j.get("location")
        info = "".join(j.get("content"))
        a = html.fromstring(info)
        page_url = "https://www.kfc.rs/restorani/"
        location_name = j.get("title")
        street_address = "".join(a.xpath("//strong[2]//text()")).split(",")[0].strip()
        state = b.get("state") or "<MISSING>"
        postal = b.get("postal_code") or "<MISSING>"
        country_code = b.get("country")
        city = b.get("city")
        store_number = j.get("id")
        latitude = b.get("lat")
        longitude = b.get("lng")
        phone = "".join(a.xpath("//strong[3]//text()"))
        hours_of_operation = (
            " ".join(a.xpath("//*//text()"))
            .replace("\r\n", "")
            .split("Radno vreme")[1]
            .strip()
        )
        if hours_of_operation.find("Preuzimanje") != -1:
            hours_of_operation = hours_of_operation.split("Preuzimanje")[0].strip()
        if hours_of_operation.find("Dostava") != -1:
            hours_of_operation = hours_of_operation.split("Dostava")[0].strip()
        if hours_of_operation.find("Drive") != -1:
            hours_of_operation = hours_of_operation.split("Drive")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace(": ", "").replace("restorana", "").strip()
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
