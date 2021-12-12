from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.com.vn"
    api_url = "https://johnsonfitness.com.vn/he-thong-cua-hang/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[./div/h2[text()="Cửa hàng"]]/following-sibling::section//div[@class="elementor-icon-box-content"]'
    )
    for d in div:

        page_url = "https://johnsonfitness.com.vn/he-thong-cua-hang/"
        location_name = "".join(d.xpath(".//h6//text()")).replace("\n", "").strip()
        street_address = "".join(d.xpath(".//p[1]/text()[1]")).replace("\n", "").strip()
        country_code = "VN"
        city = "".join(d.xpath(".//preceding::h5[1]//text()"))
        phone = (
            "".join(d.xpath(".//p[1]/text()[2]"))
            .replace("\n", "")
            .replace("ĐT:", "")
            .strip()
        )

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
