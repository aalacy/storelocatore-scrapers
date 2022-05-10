from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.superaiello.com.ar/"
    page_url = "https://www.superaiello.com.ar/sucursales.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="sucursal"]')
    for d in div:

        location_name = "".join(d.xpath(".//strong//text()"))
        street_address = (
            "".join(d.xpath(".//strong/following-sibling::text()"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "AR"
        city = " ".join(location_name.split()[1:]).strip()
        ll = "".join(d.xpath(".//button/@onclick")).replace("'", "").strip()
        latitude = ll.split("(")[1].split(",")[0].strip()
        longitude = ll.split("(")[1].split(",")[1].split(")")[0].strip()

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
