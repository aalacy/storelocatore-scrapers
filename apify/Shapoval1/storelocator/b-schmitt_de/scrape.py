from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.b-schmitt.de/"
    api_url = "https://www.b-schmitt.de/standorte/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Informieren"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        ad = tree.xpath(
            '//h4[./span[text()="Anschrift"]]/following-sibling::div[1]/p/text()'
        )
        ad = list(filter(None, [a.strip() for a in ad]))
        street_address = " ".join(ad[:-1]).strip()
        adr = "".join(ad[-1]).strip()
        state = "<MISSING>"
        postal = adr.split()[0].strip()
        country_code = "DE"
        city = " ".join(adr.split()[1:])
        phone = (
            " ".join(
                tree.xpath(
                    '//h4[./span[text()="Kontakt"]]/following-sibling::div[1]/p//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = " ".join(phone.split()).replace("Tel.:", "").strip()
        if phone.find("Fax:") != -1:
            phone = phone.split("Fax:")[0].strip()
        hours_of_operation = (
            " ".join(tree.xpath("//table//tr//td//text()"))
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
            raw_address=f"{street_address} {adr}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
