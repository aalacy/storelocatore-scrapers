from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dennysdiners.co.uk"
    api_url = "https://dennysdiners.co.uk/find-us/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    page_url = "https://dennysdiners.co.uk/find-us/"
    location_name = (
        "".join(tree.xpath('//li[./span/i[@class="fas fa-map-pin"]]/span[2]/text()[1]'))
        .replace("\n", "")
        .replace(",", "")
        .strip()
        or "<MISSING>"
    )
    street_address = (
        "".join(tree.xpath('//li[./span/i[@class="fas fa-map-pin"]]/span[2]/text()[2]'))
        .replace("\n", "")
        .replace(",", "")
        .strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath('//li[./span/i[@class="fas fa-map-pin"]]/span[2]/text()[4]'))
        .replace("\n", "")
        .replace(",", "")
        .strip()
        or "<MISSING>"
    )
    country_code = "UK"
    city = (
        "".join(tree.xpath('//li[./span/i[@class="fas fa-map-pin"]]/span[2]/text()[3]'))
        .replace("\n", "")
        .replace(",", "")
        .strip()
        or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath('//a[contains(@href, "tel")]//text()'))
        .replace("\n", "")
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
        hours_of_operation=SgRecord.MISSING,
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
