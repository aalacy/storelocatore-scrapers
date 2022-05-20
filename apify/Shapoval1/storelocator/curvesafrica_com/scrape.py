import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.curvesafrica.com/"
    api_url = "https://www.curvesafrica.com/find-your-curves-club/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "curves_locations =")]/text()'))
        .split("curves_locations = ")[1]
        .strip()
    )
    js = json.loads(js_block)
    for j in js.values():

        page_url = "".join(j.get("mp_meta").get("permalink"))
        location_name = j.get("post_title")
        street_address = " ".join(j.get("mp_meta").get("single_address"))
        postal = " ".join(j.get("mp_meta").get("single_zip"))
        if postal == "n/a":
            postal = "<MISSING>"
        country_code = " ".join(j.get("mp_meta").get("cc"))
        city = " ".join(j.get("mp_meta").get("single_city"))
        store_number = j.get("ID")
        latitude = " ".join(j.get("mp_meta").get("latitude"))
        longitude = " ".join(j.get("mp_meta").get("longitude"))
        phone = " ".join(j.get("mp_meta").get("phone"))
        hours = " ".join(j.get("mp_meta").get("openinghours"))
        hours_of_operation = "<MISSING>"
        if hours:
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
            state=SgRecord.MISSING,
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
