import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bonpreuesclat.cat/"
    api_url = "https://www.bonpreuesclat.cat/cercador-d-establiments"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "var establimentsJson")]/text()'))
        .split("ar establimentsJson = ")[1]
        .split("function")[0]
        .replace("\n", "")
        .strip()
    )
    js = json.loads(js_block)
    for j in js:

        location_name = j.get("descripcio") or "<MISSING>"
        location_type = j.get("tipus") or "<MISSING>"
        street_address = j.get("direccio") or "<MISSING>"
        postal = j.get("codiPostal") or "<MISSING>"
        country_code = "ES"
        city = j.get("poblacio") or "<MISSING>"
        store_number = j.get("codi") or "<MISSING>"
        latitude = j.get("latitud") or "<MISSING>"
        longitude = j.get("longitud") or "<MISSING>"
        phone = j.get("telefon") or "<MISSING>"
        slug = j.get("page")
        page_url = f"https://www.bonpreuesclat.cat{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="horariItem"]/div[1]//text() | //div[@class="horariItem"]/div[3]//text()'
                )
            )
            .replace("\n", "")
            .strip()
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
            location_type=location_type,
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
