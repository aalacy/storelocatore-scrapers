import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://littlegreekfreshgrill.com/"
    api_url = "https://littlegreekfreshgrill.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[@class="menu-item-title"]')
    for d in div:

        page_url = "".join(d.xpath(".//a/@href"))
        street_address = (
            "".join(d.xpath(".//following-sibling::div[1]//text()")) or "<MISSING>"
        )
        ad = (
            "".join(d.xpath(".//following-sibling::div[2]//text()"))
            .replace("FL, FL", "FL")
            .strip()
            or "<MISSING>"
        )
        if ad == ",":
            ad = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        if ad != "<MISSING>":
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[1].strip()

        phone = "".join(d.xpath(".//following-sibling::div[3]//text()")) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        js_block = "".join(tree.xpath('//script[contains(text(), "address")]/text()'))
        js = json.loads(js_block)
        a = js.get("address")
        if state == "<MISSING>":
            state = a.get("addressRegion")
        location_name = "".join(tree.xpath("//title//text()")) or "<MISSING>"
        hours_of_operation = (
            " ".join(tree.xpath('//div[@id="store_hours_of_operation"]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
