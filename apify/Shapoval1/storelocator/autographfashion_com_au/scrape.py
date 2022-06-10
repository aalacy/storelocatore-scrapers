from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.autographfashion.com.au"
    api_url = "https://www.autographfashion.com.au/Store.xml"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = tree.xpath('//h4[text()="Address"]/following-sibling::p[1]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        js_block = "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))

        street_address = "<MISSING>"
        if len(ad) == 5:
            street_address = "".join(ad[1]).strip()
        if len(ad) == 4:
            street_address = "".join(ad[0]).strip()
        if street_address == "1":
            street_address = "<MISSING>"
        city = js_block.split('"addressLocality": "')[1].split('"')[0].strip()
        state = js_block.split('"addressRegion": "')[1].split('"')[0].strip()
        postal = "".join(ad[-1]).strip()
        country_code = "AU"
        if state == "NZ":
            country_code = "NZ"
        location_name = js_block.split('"name": "')[1].split('"')[0].strip()
        phone = (
            "".join(tree.xpath('//span[contains(text(), "Phone")]/text()'))
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[text()="Opening Hours"]/following-sibling::*[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        latitude = js_block.split('"latitude": "')[1].split('"')[0].strip()
        longitude = js_block.split('"longitude": "')[1].split('"')[0].strip()
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"

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
            raw_address=" ".join(ad),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
