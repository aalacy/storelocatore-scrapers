from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.triumphmotorcycles.cl"
    page_url = "https://www.triumphmotorcycles.cl/contactenos.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="cta-content"]/h2')
    for d in div:

        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        street_address = "".join(d.xpath(".//following-sibling::p[1]/a[1]/text()"))
        info = d.xpath(".//following-sibling::p[1]/text()")
        city = "<MISSING>"
        if "Las Condes" in street_address:
            city = "Las Condes"
        if "VIÑA DEL MAR" in location_name:
            city = "VIÑA DEL MAR"
        country_code = "CL"
        phone = "".join(d.xpath(".//following-sibling::p[1]/a[2]/text()"))
        tmp = []
        for i in info:
            if "Lun" in i:
                tmp.append(i)
                break
        hours_of_operation = "".join(tmp).replace("\n", "").strip()
        location_type = (
            "".join(d.xpath(".//following-sibling::p[1]/b[2]/text()"))
            .replace(":", "")
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
            location_type=location_type,
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
