import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.bonchonthailand.com/"
    page_url = "http://www.bonchonthailand.com/index.php?route=custompages/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var shops =")]/text()'))
        .split("var shops =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:

        location_name = "".join(j.get("name")).replace("_", " ").capitalize().strip()
        if location_name != "Bangkok":
            location_name = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('comment')}".replace(
            "@ ", ""
        ).strip()
        country_code = "TH"
        city = location_name
        if city != "Bangkok":
            city = "<MISSING>"
        try:
            latitude = "".join(j.get("geocode")).split(",")[0].strip()
            longitude = "".join(j.get("geocode")).split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
