from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://skemman.fo/"
    page_url = "https://skemman.fo/ymiskt/kunning/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()"))
    street_address = (
        "".join(
            tree.xpath(
                '//span[contains(text(), "Um Skemmuna")]/following-sibling::ul/li[2]/text()'
            )
        )
        .replace("-", "")
        .replace(",", "")
        .strip()
    )
    ad = (
        "".join(
            tree.xpath(
                '//span[contains(text(), "Um Skemmuna")]/following-sibling::ul/li[3]/text()'
            )
        )
        .replace("-", "")
        .replace(",", "")
        .strip()
    )
    postal = ad.split()[0].strip()
    country_code = "FO"
    city = ad.split()[1].strip()
    phone = (
        "".join(
            tree.xpath(
                '//span[contains(text(), "Um Skemmuna")]/following-sibling::ul/li[4]/text()'
            )
        )
        .replace("-", "")
        .replace("Tlf:", "")
        .replace(",", "")
        .strip()
    )
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//span[text()="Upplatingartíðir"]/following-sibling::div[1]/ul/li[position() < last() - 1]//text()'
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
        state=SgRecord.MISSING,
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
