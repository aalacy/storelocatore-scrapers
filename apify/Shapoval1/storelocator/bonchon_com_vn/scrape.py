from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bonchon.com.vn/"
    page_url = "https://bonchon.com.vn/contact"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[./label[contains(text(), "Cửa hàng")]]')
    for d in div:

        location_name = "".join(d.xpath(".//label/text()")).replace(":", "").strip()
        street_address = (
            "".join(d.xpath(".//label/following-sibling::text()")).split("-")[0].strip()
        )
        if street_address.find("–") != -1:
            street_address = street_address.split("–")[0].strip()
        country_code = "VN"
        city = (
            "".join(d.xpath(".//preceding-sibling::p[not(text())][1]//text()"))
            .replace(":", "")
            .strip()
        )
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if street_address.find("12") != -1:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        ad = "".join(d.xpath(".//label/following-sibling::text()"))
        phone = "<MISSING>"
        if ad.find("-") != -1:
            phone = ad.split("-")[1].strip()
        if ad.find("–") != -1:
            phone = ad.split("–")[1].strip()
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/following::label[contains(text(), "Giờ mở cửa:")]/following-sibling::text()'
                )
            )
            .replace("\n", "")
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
