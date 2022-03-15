from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://metropolitanbakery.com/"
    page_url = "https://metropolitanbakery.com/pages/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./h2[@class="h3"]]')

    for d in div:

        location_name = "".join(d.xpath('.//h2[@class="h3"]/text()'))
        street_address = "".join(d.xpath('.//h3[@class="h4"]/text()'))
        phone = (
            "".join(d.xpath('.//div/p/strong[contains(text(), "-")]/text()'))
            or "<MISSING>"
        )
        country_code = "US"
        ll = "".join(d.xpath('.//a[contains(text(), "View Map")]/@href'))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll:
            latitude = ll.split("ll=")[1].split(",")[0].strip()
            longitude = ll.split("ll=")[1].split(",")[1].split("&")[0].strip()
        hours_of_operation = (
            "".join(d.xpath(".//div/p[1]//text()")).replace("*", "").strip()
        )
        if hours_of_operation.find("Hours") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("215") != -1:
            hours_of_operation = hours_of_operation.split("215")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
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
