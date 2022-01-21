import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.noanoahawaii.com/"
    api_url = "https://www.noanoahawaii.com/contact-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h2]")
    for d in div:

        page_url = "https://www.noanoahawaii.com/contact-us"
        location_name = "".join(d.xpath(".//h2/text()"))
        street_address = "".join(d.xpath(".//h3[1]/text()"))
        ad = "".join(d.xpath(".//h3[2]/text()"))
        state = ad.split()[1].strip()
        postal = ad.split()[2].strip()
        country_code = "US"
        city = ad.split()[0].strip()
        jsblock = "".join(
            d.xpath(".//following::div[@data-block-json][1]/@data-block-json")
        )
        js = json.loads(jsblock)
        latitude = js.get("location").get("mapLat") or "<MISSING>"
        longitude = js.get("location").get("mapLng") or "<MISSING>"
        phone = "".join(d.xpath('./*[contains(text(), "808")]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//p[contains(text(), "pm")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
