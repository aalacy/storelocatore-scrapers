from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.chilis.com.ec/"
    api_url = "https://www.chilis.com.ec/reservas/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[.//a[contains(text(), "Ver mapa")]]')
    for d in div:

        page_url = "https://www.chilis.com.ec/reservas/"
        location_name = (
            " ".join(d.xpath(".//preceding::p[2]/strong/text()"))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if location_name == "<MISSING>":
            location_name = (
                " ".join(d.xpath(".//preceding::p[2]/text()[1]"))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        if location_name == "<MISSING>":
            location_name = (
                "".join(d.xpath(".//preceding::p[3]/strong/text()"))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        street_address = (
            " ".join(d.xpath(".//preceding::p[2]/text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            street_address = "".join(
                d.xpath(".//preceding::p[3]/strong/following-sibling::text()")
            )
        street_address = street_address.replace(f"{location_name}", "").strip()
        country_code = "Ecuador"
        city = "".join(d.xpath(".//preceding::h4[1]//text()"))
        phone = "".join(d.xpath(".//preceding::p[1]/text()[1]"))
        hours_of_operation = (
            " ".join(
                d.xpath(
                    f'.//following::h4/span[contains(text(), "{city}")]/following::p[./strong/span[contains(text(), "Dine-in")]][1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        f'.//following::h4/span[contains(text(), "{city}")]/following::p[./span/strong[contains(text(), "Dine-in")]][1]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
        hours_of_operation = hours_of_operation.replace("Dine-in", "").strip()

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
