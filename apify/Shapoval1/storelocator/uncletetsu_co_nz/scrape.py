from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://uncletetsu.co.nz"
    page_url = "https://uncletetsu.co.nz/contact-us/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = "".join(
        tree.xpath('//h3[text()="Location"]/following-sibling::p[1]/text()[1]')
    )
    ad = (
        "".join(tree.xpath('//h3[text()="Location"]/following-sibling::p[1]/text()[2]'))
        .replace("\n", "")
        .strip()
    )
    state = ad.split(",")[1].strip()
    postal = (
        "".join(tree.xpath('//h3[text()="Location"]/following-sibling::p[1]/text()[3]'))
        .replace("\n", "")
        .replace("PIN:", "")
        .strip()
    )
    country_code = "NZ"
    city = ad.split(",")[0].strip()
    map_link = "".join(tree.xpath("//iframe/@src"))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3[./strong[text()="Opening Hours"]]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    tmp_hoo = (
        " ".join(
            tree.xpath(
                '//p[contains(text(), "Temporary Opening Hours")]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    if tmp_hoo:
        hours_of_operation = tmp_hoo

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=SgRecord.MISSING,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=SgRecord.MISSING,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        hours_of_operation=hours_of_operation,
        raw_address=f"{street_address} {ad} {postal}",
    )

    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
