from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.chichispizza.com"
    api_url = "https://www.chichispizza.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h2]")
    for d in div:
        page_url = "https://www.chichispizza.com/locations"
        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()

        street_address = "".join(d.xpath(".//following-sibling::div[1]/p[1]/text()"))
        ad = "".join(d.xpath(".//following-sibling::div[1]/p[2]/text()"))
        if street_address.find("(") != -1:
            street_address = "".join(
                d.xpath(".//following-sibling::div[1]/p[2]/text()")
            )
            ad = "".join(d.xpath(".//following-sibling::div[1]/p[3]/text()"))
        phone = "".join(
            d.xpath('.//following-sibling::div[1]//a[contains(@href, "tel")]//text()')
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::p[./span[text()="HOURS"]]/following-sibling::p[position()>1]//text()'
                )
            )
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
