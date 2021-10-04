from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wildflowerbread.com"
    api_url = "https://wildflowerbread.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="eight columns locations"]/div[@class="row"]')
    for b in block:

        street_address = "".join(
            b.xpath('.//span[@itemprop="streetAddress"][2]/text()')
        )
        city = "".join(b.xpath('.//span[@itemprop="addressLocality"]/text()'))
        postal = "".join(b.xpath('.//span[@itemprop="postalCode"]/text()'))
        state = "".join(b.xpath('.//span[@itemprop="addressRegion"]/text()'))
        country_code = "US"
        location_name = "".join(b.xpath('.//span[@itemprop="name"]/a/text()'))
        if location_name.find("Airport") != -1:
            street_address = "".join(
                b.xpath('.//span[1][@itemprop="streetAddress"]/text()')
            )
        slug = "".join(b.xpath('.//span[@itemprop="name"]/a/@href'))
        page_url = f"{locator_domain}{slug}"
        phone = "".join(b.xpath('.//a[@itemprop="telephone"]/text()'))
        if location_name.find("Closed") != -1:
            location_name = location_name.split("-")[1].split("-")[0].strip()
        percls = "".join(b.xpath('.//p[contains(text(), "permanently closed")]/text()'))
        if percls:
            continue

        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        try:
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "centerMap")]/text()'))
                .split("LatLng(")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "centerMap")]/text()'))
                .split("LatLng(")[1]
                .split(",")[1]
                .split(")")[0]
                .strip()
            )
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

        hours_of_operation = (
            " ".join(tree.xpath('//time[@itemprop="openingHours"]/text()'))
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
