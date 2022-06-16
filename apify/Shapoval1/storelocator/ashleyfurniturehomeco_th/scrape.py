import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://store.ashleyfurniturehomestore.co.th/"
    api_url = "https://store.ashleyfurniturehomestore.co.th/contact"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath('//input[@id="address_data"]/@value'))
    js = json.loads(div)
    for j in js:

        page_url = "https://store.ashleyfurniturehomestore.co.th/contact"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zipcode") or "<MISSING>"
        country_code = "TH"
        city = str(j.get("city")) or "<MISSING>"
        if city.find(",") != -1:
            city = city.split(",")[0].strip()
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("contact") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("storeHours") or "<MISSING>"
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
