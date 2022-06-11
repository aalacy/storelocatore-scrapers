from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.newbalance.co.il/"
    api_url = "https://www.newbalance.co.il/articles/NBISRAELSTORES"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//*[contains(text(), "שעות פתיחה:")]')
    for d in div:

        page_url = "https://www.newbalance.co.il/articles/NBISRAELSTORES"
        location_name = "New Balance Store"
        ad = "".join(d.xpath(".//preceding::span[1]//text()"))
        street_address = ad.split("|")[0].replace("חנות היבואן:", "").strip()
        country_code = "IL"
        city = "".join(d.xpath(".//preceding::strong[1]//text()"))
        phone = ad.split("|")[1].replace("טלפון:", "").strip()
        hours_of_operation = "".join(d.xpath(".//following::span[1]//text()"))
        if street_address.find("3") != -1:
            hours_of_operation = (
                hours_of_operation
                + " "
                + "".join(d.xpath(".//following::span[2]//text()"))
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
