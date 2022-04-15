from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://carlsjr.com.ec/"
    page_url = "https://carlsjr.com.ec/index.php?option=com_content&view=category&layout=blog&id=6&Itemid=8"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@style="margin-left:30px;"]/ul/li')
    for d in div:

        street_address = " ".join(d.xpath(".//text()")).replace("\n", "").strip()
        street_address = " ".join(street_address.split())
        if street_address.find("Teléfono:") != -1:
            street_address = street_address.split("Teléfono:")[0].strip()
        country_code = "EC"
        city = "".join(d.xpath(".//preceding::p[1]//text()")).strip()
        location_name = city
        phone = (
            "".join(d.xpath(".//strong/following-sibling::text()"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if phone.find("-") != -1:
            phone = phone.split("-")[0].strip()

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
