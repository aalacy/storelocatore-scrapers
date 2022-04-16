from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pitapit.se/"
    api_url = "https://pitapit.se/hitta-restaurang/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2[contains(text(), "Pita")]')
    for d in div:

        page_url = "https://pitapit.se/hitta-restaurang/"
        location_name = "".join(d.xpath(".//text()"))
        street_address = (
            "".join(d.xpath(".//following::p[1]/text()[1]")).replace("\n", "").strip()
        )
        ad = "".join(d.xpath(".//following::p[1]/text()[2]")).replace("\n", "").strip()
        postal = " ".join(ad.split()[:-1]).strip()
        country_code = "SE"
        city = "".join(ad.split()[-1]).strip()
        phone = (
            "".join(d.xpath(".//following::p[1]/text()[3]"))
            .replace("\n", "")
            .replace("T:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::p[./strong[text()="ÖPPETTIDER"]][1]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
