from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.reanimatorcoffee.com"
    page_url = "https://www.reanimatorcoffee.com/pages/locations"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-info"]')
    for d in div:

        location_name = "".join(d.xpath(".//h2/text()"))
        street_address = "".join(d.xpath(".//h3/text()"))
        country_code = "US"
        text = "".join(d.xpath('.//a[text()="GET DIRECTIONS"]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="hours"]/p//text()'))
            .replace("\n", " ")
            .strip()
        )
        if hours_of_operation.find("Call") != -1:
            hours_of_operation = "<MISSING>"
        phone = "".join(d.xpath('.//a[@class="phone-number"]/text()'))

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
