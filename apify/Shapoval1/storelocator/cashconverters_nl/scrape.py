from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cashconverters.nl"
    page_url = "https://cashconverters.nl/winkels/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div/h4/strong]")
    for d in div:

        location_name = "".join(d.xpath(".//preceding-sibling::div[1]//h3//text()"))
        info = d.xpath(
            './/h4[./strong[text()="Adres"]]/following-sibling::p[1]//text()'
        )
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(info[0]).strip()
        ad = "".join(info[1]).strip()
        postal = ad.split()[0].strip()
        country_code = "NL"
        city = " ".join(ad.split()[1:])
        phone = "".join(info[2]).replace("tel:", "").strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/h4[./strong[text()="Winkeltijden"]]/following-sibling::table//tr//td//text()'
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
            raw_address=f"{street_address} {city} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
