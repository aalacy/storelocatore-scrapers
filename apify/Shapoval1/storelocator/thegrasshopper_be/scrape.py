from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.thegrasshopper.be/"
    page_url = "https://www.thegrasshopper.be/contact"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h6[./span[contains(text(), "The Grasshopper")]]')
    for d in div:

        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        street_address = "".join(d.xpath(".//following::span[text()][1]//text()"))
        ad = "".join(d.xpath(".//following::span[text()][2]//text()"))
        postal = ad.split()[0].strip()
        country_code = "BE"
        city = ad.split()[1].strip()
        phone = (
            "".join(d.xpath(".//following::span[text()][3]//text()"))
            .replace("Tel.:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath(".//following-sibling::p//text()"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .split(".be")[1]
            .split("Opgelet")[0]
            .replace("(Enkel gesloten op 25 december en 1 januari) ​", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
