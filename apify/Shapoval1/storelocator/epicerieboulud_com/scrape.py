from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.epicerieboulud.com"
    api_url = "https://www.epicerieboulud.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(@class, "Header-nav-folder-item")][position()>1]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        page_url = f"{locator_domain}{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1//text()"))
        street_address = "".join(tree.xpath("//h1/following-sibling::p[1]/text()[1]"))
        ad = (
            "".join(tree.xpath("//h1/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = "".join(
            tree.xpath('//h1/following-sibling::p/a[contains(@href, "tel")]/text()')
        )
        hours_of_operation = (
            " ".join(tree.xpath("//div[./h1]//text()")).replace("\n", "").strip()
            or "<MISSING>"
        )
        try:
            hours_of_operation = hours_of_operation.split(f"{phone}")[1].strip()
        except IndexError:
            hours_of_operation = "<MISSING>"
        cms = "".join(tree.xpath('//strong[text()="REOPENING SOON"]/text()'))
        if cms:
            hours_of_operation = "Temporarily closed"

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
            raw_address=street_address + " " + ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
