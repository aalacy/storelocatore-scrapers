import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://kfcbrasil.com.br"
    page_url = "https://kfcbrasil.com.br/enderecos/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[./a[@class="lname"]]')

    for d in div:

        location_name = "".join(d.xpath('.//a[@class="lname"]/text()'))
        if not location_name:
            continue
        street_address = "".join(d.xpath('.//div[@class="end1"]/text()')).strip()
        ad = "".join(d.xpath('.//div[@class="end2"]/text()')).strip() or "<MISSING>"
        if ad == "<MISSING>":
            street_address = "<MISSING>"
            ad = "".join(d.xpath('.//div[@class="end1"]/text()')).strip()
        a = parse_address(International_Parser(), ad)
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "BR"
        city = a.city or "<MISSING>"
        if "Monções" in ad:
            city = "Monções"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "".join(d.xpath(".//small/text()"))
        js_block = (
            "".join(
                tree.xpath('//script[contains(text(), "const locations =")]/text()')
            )
            .split("const locations =")[1]
            .split(";")[0]
            .strip()
        )
        js = json.loads(js_block)
        for j in js:
            name = j.get("name")
            if location_name == name:
                latitude = "".join(j.get("lat"))
                longitude = "".join(j.get("lng"))
                if longitude.find(".") == -1:
                    longitude = longitude[:3] + "." + longitude[3:]

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}".replace("<MISSING>", "").strip(),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)
