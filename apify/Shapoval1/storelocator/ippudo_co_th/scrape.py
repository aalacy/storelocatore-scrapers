from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ippudo.co.th"
    page_url = "https://ippudo.co.th/store/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="storebox"]')
    for d in div:

        location_name = "".join(d.xpath("./@data-title"))
        location_type = "".join(
            d.xpath('.//preceding::p[@class="storetype"][1]/text()')
        )
        street_address = (
            location_name + " " + "".join(d.xpath('.//p[@class="storefloor"]/text()'))
        )
        country_code = "TH"
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))
        phone = (
            " ".join(
                d.xpath('.//div[@class="storeright"]/p[@class="storetime"]/text()')
            )
            .replace("\n", "")
            .replace("call", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="storeleft"]/p[@class="storetime"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

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
            location_type=location_type,
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
